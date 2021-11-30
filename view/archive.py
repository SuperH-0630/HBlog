from flask import Flask, Blueprint, render_template, abort, redirect, url_for, flash
from typing import Optional
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from view.base import App
from core.user import User
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
    return render_template("archive/archive.html", archive_list=archive_list, form=CreateArchiveForm())


@archive.route("create-archive", methods=["POST"])
@login_required
def create_archive_page():
    form = CreateArchiveForm()
    if form.validate_on_submit():
        auth: User = current_user
        if not auth.check_role("WriteBlog"):  # 检查相应的权限
            abort(403)
            return

        if Archive(form.name.data, form.describe.data, None).create():
            flash(f"创建归档 {form.name.data} 成功")
        else:
            flash(f"创建归档 {form.name.data} 失败")
        return redirect(url_for("archive.archive_page"))
    abort(404)


@archive.context_processor
def inject():
    return {"top_nav": ["", "active", "", "", "", ""]}


class ArchiveApp(App):
    def __init__(self, import_name):
        super(ArchiveApp, self).__init__(import_name)

        global app
        app = self._app
        app.register_blueprint(archive, url_prefix="/archive")
