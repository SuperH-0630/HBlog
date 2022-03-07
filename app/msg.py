from flask import Blueprint, render_template, abort, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired

import app
from sql.base import DBBit
from object.msg import Message, load_message_list

msg = Blueprint("msg", __name__)


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
        app.HBlogFlask.print_user_opt_fail_log(f"Load msg list with error page({page})")
        abort(404)
        return

    msg_list = load_message_list(20, (page - 1) * 20,
                                 show_secret=current_user.check_role("ReadSecretMsg"))  # 判断是否可读取私密内容
    max_page = app.HBlogFlask.get_max_page(Message.get_msg_count(), 20)
    page_list = app.HBlogFlask.get_page("docx.docx_page", page, max_page)
    app.HBlogFlask.print_load_page_log(f"msg (page: {page})")
    return render_template("msg/msg.html",
                           msg_list=msg_list,
                           page_list=page_list,
                           form=WriteForm(),
                           is_secret=DBBit.BIT_1,
                           show_delete=current_user.check_role("DeleteMsg"),
                           show_email=current_user.check_role("ReadUserInfo"))


@msg.route('/write', methods=["POST"])
@login_required
@app.form_required(WriteForm, "write msg")
@app.role_required("WriteMsg", "write msg")
def write_msg_page(form: WriteForm):
    context = form.context.data
    secret = form.secret.data
    if Message(None, current_user, context, secret, None).create():
        app.HBlogFlask.print_user_opt_success_log("write msg")
        flash("留言成功")
    else:
        app.HBlogFlask.print_user_opt_fail_log("write msg")
        flash("留言失败")
    return redirect(url_for("msg.msg_page", page=1))


@msg.route('/delete/<int:msg_id>')
@login_required
@app.role_required("DeleteMsg", "delete msg")
def delete_msg_page(msg_id: int):
    if Message(msg_id, None, None).delete():
        app.HBlogFlask.print_user_opt_success_log("delete msg")
        flash("留言删除成功")
    else:
        app.HBlogFlask.print_user_opt_fail_log("delete msg")
        flash("留言删除失败")
    return redirect(url_for("msg.msg_page", page=1))


@msg.context_processor
def inject_base():
    return {"top_nav": ["", "", "", "active", "", ""]}