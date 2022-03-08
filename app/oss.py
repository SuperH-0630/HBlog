from flask import Blueprint, redirect, render_template, abort, flash, url_for, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from aliyun import aliyun
import app

oss = Blueprint("oss", __name__)


class UploadForm(FlaskForm):
    file = FileField("选择文件", description="待上传文件",
                     validators=[DataRequired(message="必须选择文件")])
    path = StringField("存储文件夹", description="文件路径(不含文件名)",
                       validators=[Length(-1, 30, message="文件路径长度为30个字符以内")])
    submit = SubmitField("上传")

    def __init__(self):
        super(UploadForm, self).__init__()
        self.path.data = "hblog/"


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
@app.role_required("ConfigureSystem", "upload file")
def upload_page():
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
