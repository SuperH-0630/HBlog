from flask import Blueprint, render_template, abort, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import app
from object.archive import Archive

archive = Blueprint("archive", __name__)


class CreateArchiveForm(FlaskForm):
    name = StringField("名字", validators=[DataRequired()])
    describe = StringField("描述", validators=[DataRequired()])
    submit = SubmitField("创建归档")


@archive.route('/')
def archive_page():
    archive_list = Archive.get_archive_list()
    app.HBlogFlask.print_load_page_log("archive list")
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
            app.HBlogFlask.print_user_not_allow_opt_log("Create archive")
            abort(403)
            return

        name = form.name.data
        describe = form.describe.data
        if len(name) > 10:
            flash("归档名太长了")
        elif len(describe) > 30:
            flash("归档描述太长了")
        else:
            if Archive(name, describe, None).create():
                app.HBlogFlask.print_sys_opt_success_log(f"Create archive {name}")
                flash(f"创建归档 {name} 成功")
            else:
                app.HBlogFlask.print_sys_opt_fail_log(f"Create archive {name}")
                flash(f"创建归档 {name} 失败")
        return redirect(url_for("archive.archive_page"))
    current_app.logger.warning("Create archive with error form.")
    abort(404)


@archive.route("delete/<int:archive_id>")
@login_required
def delete_archive_page(archive_id: int):
    if not current_user.check_role("DeleteBlog"):
        app.HBlogFlask.print_user_not_allow_opt_log("Delete archive")
        abort(403)
        return

    if Archive(None, None, archive_id).delete():
        app.HBlogFlask.print_sys_opt_success_log(f"Delete archive {archive_id}")
        flash("归档删除成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log(f"Delete archive {archive_id}")
        flash("归档删除失败")
    return redirect(url_for("archive.archive_page"))


@archive.context_processor
def inject():
    return {"top_nav": ["", "active", "", "", "", ""]}
