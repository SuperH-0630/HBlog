from flask import Flask, Blueprint, redirect, render_template, abort, flash, url_for, request
from flask_login import login_required, current_user
from typing import Optional
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

from aliyun import aliyun
from view.base import App

oss = Blueprint("oss", __name__)
app: Optional[Flask] = None


class UploadForm(FlaskForm):
    file = FileField("选择文件", validators=[DataRequired()])
    submit = SubmitField("上传")


@oss.before_request
def check_aliyun():
    if aliyun is None:
        OSSApp.print_user_opt_fail_log("aliyun not used")
        abort(404)
        return


@oss.route('get/<string:name>')
def get_page(name: str):
    OSSApp.print_user_opt_success_log(f"get file {name}")
    return redirect(aliyun.shared_obj(name))


@oss.route('upload', methods=["GET", "POST"])
@login_required
def upload_page():
    if not current_user.check_role("ConfigureSystem"):
        OSSApp.print_user_not_allow_opt_log("upload file")
        abort(403)
        return

    form = UploadForm()
    if form.validate_on_submit():
        file = request.files["file"]
        aliyun.upload_file(file.filename, file)
        OSSApp.print_sys_opt_success_log(f"Upload file {file.filename}")
        flash(f"文件 {file.filename} 已上传: {url_for('oss.get_page', name=file.filename, _external=True)}")
        return redirect(url_for("oss.upload_page"))
    OSSApp.print_load_page_log(f"OSS upload")
    return render_template("oss/upload.html", UploadForm=form)


class OSSApp(App):
    def __init__(self, import_name):
        super(OSSApp, self).__init__(import_name)

        global app
        app = self._app
        app.register_blueprint(oss, url_prefix="/oss")
