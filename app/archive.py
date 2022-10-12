from flask import Blueprint, render_template, redirect, url_for, flash, g, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import app
from object.archive import Archive
from configure import conf

archive = Blueprint("archive", __name__)


class CreateArchiveForm(FlaskForm):
    name = StringField("名称", description="归档名称",
                       validators=[DataRequired(message="必须填写归档名称"),
                                   Length(1, 10, message="归档名称长度1-10个字符")])
    describe = TextAreaField("描述", description="归档描述",
                             validators=[Length(-1, 25, message="归档描述长度25个字符以内")])
    submit = SubmitField("创建归档")

    def validate_name(self, field):
        name = field.data
        archive_list = Archive.get_archive_list()
        for i in archive_list:
            if name == i.name:
                raise ValidationError("归档已经存在")


def __load_archive_page(form: CreateArchiveForm):
    archive_list = Archive.get_archive_list()
    app.HBlogFlask.print_load_page_log("archive list")
    return render_template("archive/archive.html",
                           archive_list=archive_list,
                           form=form,
                           show_delete=current_user.check_role("DeleteBlog"))


@archive.route('/')
def archive_page():
    return __load_archive_page(CreateArchiveForm())


@archive.route("/create", methods=["POST"])
@login_required
@app.form_required(CreateArchiveForm, "create archive", __load_archive_page)
@app.role_required("WriteBlog", "create archive")
def create_archive_page():
    form: CreateArchiveForm = g.form
    name = form.name.data
    describe = form.describe.data
    if Archive.create(name, describe):
        app.HBlogFlask.print_sys_opt_success_log(f"Create archive {name}")
        flash(f"创建归档 {name} 成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log(f"Create archive {name}")
        flash(f"创建归档 {name} 失败")
    return redirect(url_for("archive.archive_page"))


@archive.route("/delete")
@login_required
@app.role_required("DeleteBlog", "delete archive")
def delete_archive_page():
    archive_id = int(request.args.get("archive", 1))
    if Archive(archive_id).delete():
        app.HBlogFlask.print_sys_opt_success_log(f"Delete archive {archive_id}")
        flash("归档删除成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log(f"Delete archive {archive_id}")
        flash("归档删除失败")
    return redirect(url_for("archive.archive_page"))


@archive.context_processor
@app.cache.cached(timeout=conf["CACHE_EXPIRE"], key_prefix="inject_base:archive")
def inject():
    """ archive 默认模板变量 """
    return {"top_nav": ["", "active", "", "", "", ""]}
