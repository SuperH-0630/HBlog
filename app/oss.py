from flask import Blueprint, redirect, render_template, abort, flash, url_for, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField
from wtforms.validators import DataRequired

from aliyun import aliyun
import app

oss = Blueprint("oss", __name__)


class UploadForm(FlaskForm):
    file = FileField("选择文件", validators=[DataRequired()])
    path = StringField("存储路径")
    submit = SubmitField("上传")


@oss.before_request
def check_aliyun():
    if aliyun is None:
        app.HBlogFlask.print_user_opt_fail_log("aliyun not used")
        abort(404)
        return


@oss.route('get/<path:name>')
def get_page(name: str):
    app.HBlogFlask.print_user_opt_success_log(f"get file {name}")
    url = aliyun.shared_obj(name)
    if url is None:
        abort(404)
    return redirect(url)


@oss.route('upload', methods=["GET", "POST"])
@login_required
def upload_page():
    if not current_user.check_role("ConfigureSystem"):
        app.HBlogFlask.print_user_not_allow_opt_log("upload file")
        abort(403)
        return

    form = UploadForm()
    if form.validate_on_submit():
        file = request.files["file"]
        path: str = form.path.data
        if len(path) > 0 and not path.endswith('/'):
            path += "/"
        path += file.filename
        aliyun.upload_file(path, file)
        app.HBlogFlask.print_sys_opt_success_log(f"Upload file {path}")
        flash(f"文件 {file.filename} 已上传: {url_for('oss.get_page', name=path, _external=True)}")
        return redirect(url_for("oss.upload_page"))
    app.HBlogFlask.print_load_page_log(f"OSS upload")
    return render_template("oss/upload.html", UploadForm=form)
