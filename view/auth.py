from flask import Flask, Blueprint, render_template, redirect, flash, url_for, request, abort
from flask_login import login_required, login_user, current_user, logout_user
from flask_mail import Mail
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo
from typing import Optional

from view.base import App
from core.user import User, load_user_by_email
from flask_wtf import FlaskForm
from send_email import send_msg

auth = Blueprint("auth", __name__)
app: Optional[Flask] = None
mail: Optional[Mail] = None


class LoginForm(FlaskForm):
    email = StringField("邮箱", validators=[DataRequired(), Length(1, 32)])
    passwd = PasswordField("密码", validators=[DataRequired(), Length(8, 32)])
    remember = BooleanField("记住我")
    submit = SubmitField("登录")


class RegisterForm(FlaskForm):
    email = StringField("邮箱", validators=[DataRequired(), Length(1, 32)])
    passwd = PasswordField("密码", validators=[DataRequired(),
                                             EqualTo("passwd_again", message="两次输入密码不相同"),
                                             Length(8, 32)])
    passwd_again = PasswordField("重复密码", validators=[DataRequired()])
    submit = SubmitField("注册")

    def validate_email(self, field):
        if load_user_by_email(field.data) is not None:
            raise ValidationError("Email already register")


@auth.route('/yours')
@login_required
def yours_page():
    msg_count, comment_count, blog_count = current_user.count_info()
    return render_template("auth/yours.html", msg_count=msg_count, comment_count=comment_count, blog_count=blog_count)


@auth.route('/login', methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("auth.yours_page"))

    form = LoginForm()
    if form.validate_on_submit():
        user = load_user_by_email(form.email.data)
        if user is not None and user.check_passwd(form.passwd.data):
            login_user(user, form.remember.data)
            next_page = request.args.get("next")
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('base.index_page')
            flash("登陆成功")
            return redirect(next_page)
        flash("账号或密码错误")
        return redirect(url_for("auth.login_page"))
    return render_template("auth/login.html", form=form)


@auth.route('/register', methods=["GET", "POST"])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("auth.yours_page"))

    form = RegisterForm()
    if form.validate_on_submit():
        token = User.creat_token(form.email.data, form.passwd.data)
        register_url = url_for("auth.confirm_page", token=token, _external=True)
        send_msg("注册确认", mail, form.email.data, "register", register_url=register_url)
        flash("注册提交成功, 请进入邮箱点击确认注册链接")
        return redirect(url_for("base.index_page"))
    return render_template("auth/register.html", RegisterForm=form)


@auth.route('/confirm')
def confirm_page():
    token = request.args.get("token", None)
    if token is None:
        abort(404)
        return

    token = User.load_token(token)
    if token is None:
        abort(404)
        return

    if load_user_by_email(token[0]) is not None:
        abort(404)
        return

    User(token[0], token[1], None, None).create()
    flash(f"用户{token[0]}认证完成")
    return redirect(url_for("base.index_page"))


@auth.route('/logout')
def logout_page():
    logout_user()
    flash("退出登录成功")
    return redirect(url_for("base.index_page"))


@auth.context_processor
def inject_base():
    return {"top_nav": ["", "", "", "", "", "active"]}


class AuthApp(App):
    def __init__(self, import_name):
        super(AuthApp, self).__init__(import_name)

        global app, mail
        app = self._app
        mail = self.mail
        app.register_blueprint(auth, url_prefix="/auth")
        self.login_manager.login_view = "auth.login_page"

        @self.login_manager.user_loader
        def user_loader(email: str):
            return load_user_by_email(email)
