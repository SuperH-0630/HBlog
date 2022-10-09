from flask import Blueprint, render_template, abort, redirect, url_for, flash, g, request
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

import app
from sql.base import DBBit
from object.msg import Message, load_message_list

msg = Blueprint("msg", __name__)


class WriteForm(FlaskForm):
    """
    写新内容表单
    """
    content = TextAreaField("", description="留言正文",
                            validators=[
                                DataRequired("请输入留言的内容"),
                                Length(1, 100, message="留言长度1-100个字符")])
    secret = BooleanField("私密留言")
    submit = SubmitField("留言")


def __load_msg_page(page: int, form: WriteForm):
    if page < 1:
        app.HBlogFlask.print_user_opt_fail_log(f"Load msg list with error page({page})")
        abort(404)
        return

    msg_list = load_message_list(20, (page - 1) * 20,
                                 show_secret=current_user.check_role("ReadSecretMsg"))  # 判断是否可读取私密内容
    max_page = app.HBlogFlask.get_max_page(Message.get_msg_count(), 20)
    page_list = app.HBlogFlask.get_page("msg.msg_page", page, max_page)
    app.HBlogFlask.print_load_page_log(f"msg (page: {page})")
    return render_template("msg/msg.html",
                           msg_list=msg_list,
                           page=page,
                           page_list=page_list,
                           form=form,
                           is_secret=DBBit.BIT_1,
                           show_delete=current_user.check_role("DeleteMsg"),
                           show_email=current_user.check_role("ReadUserInfo"))


@msg.route('/')
def msg_page():
    page = int(request.args.get("page", 1))
    return __load_msg_page(page, WriteForm())


@msg.route('/create', methods=["POST"])
@login_required
@app.form_required(WriteForm, "write msg", lambda form: __load_msg_page(int(request.args.get("page", 1)), form))
@app.role_required("WriteMsg", "write msg")
def write_msg_page():
    form: WriteForm = g.form
    content = form.content.data
    secret = form.secret.data
    if Message.create(current_user, content, secret):
        app.HBlogFlask.print_user_opt_success_log("write msg")
        flash("留言成功")
    else:
        app.HBlogFlask.print_user_opt_fail_log("write msg")
        flash("留言失败")
    return redirect(url_for("msg.msg_page", page=1))


@msg.route('/delete')
@login_required
@app.role_required("DeleteMsg", "delete msg")
def delete_msg_page():
    msg_id = int(request.args.get("msg", 1))
    if Message(msg_id).delete():
        app.HBlogFlask.print_user_opt_success_log("delete msg")
        flash("留言删除成功")
    else:
        app.HBlogFlask.print_user_opt_fail_log("delete msg")
        flash("留言删除失败")
    return redirect(url_for("msg.msg_page", page=1))


@msg.context_processor
def inject_base():
    """ msg 默认模板变量 """
    return {"top_nav": ["", "", "", "active", "", ""]}