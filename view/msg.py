from flask import Flask, Blueprint, render_template, abort, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from typing import Optional

from view.base import App
from sql.base import DBBit
from core.user import User
from core.msg import Message, load_message_list

msg = Blueprint("msg", __name__)
app: Optional[Flask] = None


class WriteForm(FlaskForm):
    """
    写新内容表单
    """
    context = TextAreaField(validators=[DataRequired()])
    secret = BooleanField("私密留言")
    submit = SubmitField("留言")


@msg.route('/<int:page>')
def msg_page(page: int = 1):
    if page < 1:
        abort(404)
        return

    msg_list = load_message_list(20, (page - 1) * 20,
                                 show_secret=current_user.check_role("ReadSecretMsg"))  # 判断是否可读取私密内容
    max_page = App.get_max_page(Message.get_msg_count(), 20)
    page_list = App.get_page("docx.docx_page", page, max_page)
    return render_template("msg/msg.html", msg_list=msg_list, page_list=page_list, form=WriteForm(),
                           is_secret=DBBit.BIT_1)


@msg.route('/write', methods=["POST"])
@login_required
def write_page():
    form = WriteForm()
    if form.validate_on_submit():
        auth: User = current_user
        if not auth.check_role("WriteMsg"):  # 检查相应权限
            abort(403)
            return

        context = form.context.data
        secret = form.secret.data
        if Message(None, auth, context, secret, None).create():
            flash("留言成功")
        else:
            flash("留言失败")

        return redirect(url_for("msg.msg_page", page=1))
    abort(404)


@msg.context_processor
def inject_base():
    return {"top_nav": ["", "", "", "active", "", ""]}


class MsgApp(App):
    def __init__(self, import_name):
        super(MsgApp, self).__init__(import_name)

        global app
        app = self._app
        app.register_blueprint(msg, url_prefix="/msg")
