from flask import Flask, Blueprint, render_template, abort, redirect, url_for, flash, current_app, request
from typing import Optional
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from view.base import App
from core.archive import Archive

archive = Blueprint("archive", __name__)
app: Optional[Flask] = None


class CreateArchiveForm(FlaskForm):
    name = StringField("名字", validators=[DataRequired(), Length(1, 10)])
    describe = StringField("描述", validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField("创建归档")


@archive.route('/')
def archive_page():
    archive_list = Archive.get_archive_list()
    ArchiveApp.print_load_page_log("archive list")
    return render_template("archive/archive.html",
                           archive_list=archive_list,
                           form=CreateArchiveForm(),
                           show_delete=current_user.check_role("DeleteBlog"))


@archive.route("create", methods=["POST"])
@login_required
def create_archive_page():
    form = CreateArchiveForm()
    if form.validate_on_submit():
        if not current_user.check_role("WriteBlog"):  # 检查相应的权限
            ArchiveApp.print_user_not_allow_opt_log("Create archive")
            abort(403)
            return

        if Archive(form.name.data, form.describe.data, None).create():
            ArchiveApp.print_sys_opt_success_log(f"Create archive {form.name.data}")
            flash(f"创建归档 {form.name.data} 成功")
        else:
            ArchiveApp.print_sys_opt_fail_log(f"Create archive {form.name.data}")
            flash(f"创建归档 {form.name.data} 失败")
        return redirect(url_for("archive.archive_page"))
    current_app.logger.warning("Create archive with error form.")
    abort(404)


@archive.route("delete/<int:archive_id>")
@login_required
def delete_archive_page(archive_id: int):
    if not current_user.check_role("DeleteBlog"):
        ArchiveApp.print_user_not_allow_opt_log("Delete archive")
        abort(403)
        return

    if Archive(None, None, archive_id).delete():
        ArchiveApp.print_sys_opt_success_log(f"Delete archive {archive_id}")
        flash("归档删除成功")
    else:
        ArchiveApp.print_sys_opt_fail_log(f"Delete archive {archive_id}")
        flash("归档删除失败")
    return redirect(url_for("archive.archive_page"))


@archive.context_processor
def inject():
    return {"top_nav": ["", "active", "", "", "", ""]}


class ArchiveApp(App):
    def __init__(self, import_name):
        super(ArchiveApp, self).__init__(import_name)

        global app
        app = self._app
        app.register_blueprint(archive, url_prefix="/archive")
