from flask import Flask, Blueprint, render_template, abort, redirect, url_for, flash
from typing import Optional
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from view.base import App
from core.user import User
from core.file import File

file = Blueprint("file", __name__)
app: Optional[Flask] = None


class CreateFileForm(FlaskForm):
    name = StringField("名字", validators=[DataRequired(), Length(1, 10)])
    describe = StringField("描述", validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField("创建归档")


@file.route('/')
def file_page():
    file_list = File.get_file_list()
    return render_template("file/file.html", file_list=file_list, form=CreateFileForm())


@file.route("create-file", methods=["POST"])
@login_required
def create_file_page():
    form = CreateFileForm()
    if form.validate_on_submit():
        auth: User = current_user
        if not auth.check_role("WriteBlog"):  # 检查相应的权限
            abort(403)
            return

        if File(form.name.data, form.describe.data, None).create_file():
            flash(f"创建归档 {form.name.data} 成功")
        else:
            flash(f"创建归档 {form.name.data} 失败")
        return redirect(url_for("file.file_page"))
    abort(404)


@file.context_processor
def inject_base():
    return {"top_nav": ["", "active", "", "", "", ""]}


class FileApp(App):
    def __init__(self, import_name):
        super(FileApp, self).__init__(import_name)

        global app
        app = self._app
        app.register_blueprint(file, url_prefix="/file")
