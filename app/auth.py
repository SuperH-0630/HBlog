from flask import Blueprint, render_template, redirect, flash, url_for, request, abort, current_app, g
from flask_login import login_required, login_user, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import (EmailField,
                     StringField,
                     PasswordField,
                     BooleanField,
                     SelectMultipleField,
                     SelectField,
                     SubmitField,
                     ValidationError)
from wtforms.validators import DataRequired, Length, Regexp, EqualTo

import app
from object.user import User
from send_email import send_msg
from configure import conf

auth = Blueprint("auth", __name__)


class AuthField(FlaskForm):
    @staticmethod
    def email_field(name: str, description: str):
        """ 提前定义 email 字段的生成函数，供下文调用 """
        return EmailField(name, description=description,
                          validators=[
                              DataRequired(f"必须填写{name}"),
                              Length(1, 32, message=f"{name}长度1-32个字符"),
                              Regexp(r"^[a-zA-Z0-9_\.\-]+@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\.]+)+$",
                                     message=f"{name}不满足正则表达式")])

    @staticmethod
    def passwd_field(name: str, description: str):
        """ 提前定义 passwd 字段的生成函数，供下文调用 """
        return PasswordField(name, description=description,
                             validators=[
                                 DataRequired(f"必须填写{name}"),
                                 Length(8, 32, message=f"{name}长度为8-32位")])

    @staticmethod
    def passwd_again_field(name: str, description: str, passwd: str = "passwd"):
        """ 提前定义 passwd again 字段的生成函数，供下文调用 """
        return PasswordField(f"重复{name}", description=description,
                             validators=[
                                 DataRequired(message=f"必须再次填写{name}"),
                                 EqualTo(passwd, message=f"两次输入的{name}不相同")])


class EmailPasswd(AuthField):
    email = AuthField.email_field("邮箱", "用户邮箱")
    passwd = AuthField.passwd_field("密码", "用户密码")


class LoginForm(EmailPasswd):
    remember = BooleanField("记住我")
    submit = SubmitField("登录")


class RegisterForm(EmailPasswd):
    passwd_again = AuthField.passwd_again_field("密码", "用户密码")
    submit = SubmitField("注册")

    def validate_email(self, field):
        """ 检验email是否合法 """
        if User(field.data).info[2] != -1:
            raise ValidationError("邮箱已被注册")

    def validate_passwd_again(self, field):
        """ 检验两次输入的密码是否相同 """
        if field.data != self.passwd.data:
            raise ValidationError("两次输入的密码不一样")


class ChangePasswdForm(AuthField):
    old_passwd = AuthField.passwd_field("旧密码", "用户原密码")
    passwd = AuthField.passwd_field("新密码", "用户新密码")
    passwd_again = AuthField.passwd_again_field("新密码", "用户新密码")
    submit = SubmitField("修改密码")

    def validate_passwd(self, field):
        """ 检验新旧密码是否相同 """
        if field.data == self.old_passwd.data:
            raise ValidationError("新旧密码不能相同")


class DeleteUserForm(AuthField):
    email = AuthField.email_field("邮箱", "用户邮箱")
    submit = SubmitField("删除用户")

    def __init__(self):
        super(DeleteUserForm, self).__init__()
        self.email_user = None

    def validate_email(self, field):
        """ 检验用户是否存在 """
        if User(field.data).info[2] == -1:
            raise ValidationError("邮箱用户不存在")


class CreateRoleForm(AuthField):
    name = StringField("角色名称", validators=[DataRequired()])
    authority = SelectMultipleField("权限", coerce=str, choices=User.RoleAuthorize)
    submit = SubmitField("创建角色")


class RoleForm(AuthField):
    name = SelectField("角色名称", validators=[DataRequired()], coerce=int)

    def __init__(self):
        super(RoleForm, self).__init__()
        self.name_res = []
        self.name_choices = []
        for i in User.get_role_list():
            self.name_res.append(i[0])
            self.name_choices.append((i[0], i[1]))
        self.name.choices = self.name_choices

    def validate_name(self, field):
        """ 检验角色是否存在 """
        if field.data not in self.name_res:
            raise ValidationError("角色不存在")


class DeleteRoleForm(RoleForm):
    submit = SubmitField("删除角色")


class SetRoleForm(RoleForm):
    email = AuthField.email_field("邮箱", "用户邮箱")
    submit = SubmitField("设置角色")

    def __init__(self):
        super(SetRoleForm, self).__init__()
        self.email_user = None

    def validate_email(self, field):
        if User(field.data).info[2] == -1:
            raise ValidationError("邮箱用户不存在")


@auth.route('/user/yours')
@login_required
def yours_page():
    msg_count, comment_count, blog_count = current_user.count
    app.HBlogFlask.print_load_page_log("user info")
    return render_template("auth/yours.html", msg_count=msg_count, comment_count=comment_count, blog_count=blog_count)


@auth.route('/user/login', methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:  # 用户已经成功登陆
        app.HBlogFlask.print_user_not_allow_opt_log("login")
        return redirect(url_for("auth.yours_page"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User(form.email.data)
        if user.info[2] != -1 and user.check_passwd(form.passwd.data):
            login_user(user, form.remember.data)
            next_page = request.args.get("next")
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('base.index_page')
            flash("登陆成功")
            app.HBlogFlask.print_user_opt_success_log(f"login {form.email.data}")
            return redirect(next_page)
        flash("账号或密码错误")
        app.HBlogFlask.print_user_opt_fail_log(f"login {form.email.data}")
        return redirect(url_for("auth.login_page"))
    app.HBlogFlask.print_load_page_log("user login")
    return render_template("auth/login.html", form=form)


@auth.route('/user/register', methods=["GET", "POST"])
def register_page():
    if current_user.is_authenticated:
        app.HBlogFlask.print_user_not_allow_opt_log("register")
        return redirect(url_for("auth.yours_page"))

    form = RegisterForm()
    if form.validate_on_submit():
        token = User.creat_token(form.email.data, form.passwd.data)
        register_url = conf["URL_NAME"] + url_for("auth.confirm_page", token=token)
        hblog: app.Hblog = current_app
        send_msg("注册确认", hblog.mail, form.email.data, "register", register_url=register_url)
        flash("注册提交成功, 请进入邮箱点击确认注册链接")
        app.HBlogFlask.print_import_user_opt_success_log(f"register {form.email.data}")
        return redirect(url_for("base.index_page"))
    app.HBlogFlask.print_load_page_log("user register")
    return render_template("auth/register.html", RegisterForm=form)


@auth.route('/user/confirm')
def confirm_page():
    token = request.args.get("token", None)
    if token is None:
        app.HBlogFlask.print_user_opt_fail_log(f"Confirm (bad token)")
        abort(404)
        return

    token = User.load_token(token)
    if token is None:
        app.HBlogFlask.print_user_opt_fail_log(f"Confirm (bad token)")
        abort(404)
        return

    if User(token[0]).info[2] != -1:
        app.HBlogFlask.print_user_opt_fail_log(f"Confirm (bad token)")
        abort(404)
        return

    User.create(token[0], token[1])
    current_app.logger.info(f"{token[0]} confirm success")
    app.HBlogFlask.print_import_user_opt_success_log(f"confirm {token[0]}")
    flash(f"用户{token[0]}认证完成")
    return redirect(url_for("base.index_page"))


@auth.route('/user/logout')
@login_required
def logout_page():
    app.HBlogFlask.print_import_user_opt_success_log(f"logout")
    logout_user()
    flash("退出登录成功")
    return redirect(url_for("base.index_page"))


@auth.route('/user/set/passwd', methods=['GET', 'POST'])
@login_required
def change_passwd_page():
    form = ChangePasswdForm()
    if form.validate_on_submit():
        if not current_user.check_passwd(form.old_passwd.data):
            app.HBlogFlask.print_user_opt_error_log(f"change passwd")
            flash("旧密码错误")
        elif current_user.change_passwd(form.passwd.data):
            app.HBlogFlask.print_user_opt_success_log(f"change passwd")
            flash("密码修改成功")
            logout_user()
            return redirect(url_for("auth.login_page"))
        else:
            app.HBlogFlask.print_user_opt_error_log(f"change passwd")
            flash("密码修改失败")
        return redirect(url_for("auth.change_passwd_page"))
    app.HBlogFlask.print_load_page_log("user change passwd")
    return render_template("auth/passwd.html", ChangePasswdForm=form)


@auth.route('/user/delete', methods=['GET', 'POST'])
@login_required
@app.role_required("DeleteUser", "delete user")
def delete_user_page():
    form = DeleteUserForm()
    if form.validate_on_submit():
        user = form.email_user
        if user.delete():
            app.HBlogFlask.print_sys_opt_success_log(f"{current_user.email} delete user {form.email.data} success")
            flash("用户删除成功")
        else:
            app.HBlogFlask.print_sys_opt_fail_log(f"{current_user.email} delete user {form.email.data} fail")
            flash("用户删除失败")
        return redirect(url_for("auth.delete_user_page"))
    app.HBlogFlask.print_load_page_log("delete user")
    return render_template("auth/delete.html", DeleteUserForm=form)


@auth.route('/role', methods=['GET'])
@login_required
@app.role_required("ConfigureSystem", "load role setting")
def role_page():
    app.HBlogFlask.print_load_page_log("role setting")
    return render_template("auth/role.html",
                           CreateRoleForm=CreateRoleForm(),
                           DeleteRoleForm=DeleteRoleForm(),
                           SetRoleForm=SetRoleForm())


@auth.route('/role/create', methods=['POST'])
@login_required
@app.form_required(CreateRoleForm, "create role")
@app.role_required("ConfigureSystem", "create role")
def role_create_page():
    form: CreateRoleForm = g.form
    name = form.name.data
    if User.create_role(name, form.authority.data):
        app.HBlogFlask.print_sys_opt_success_log(f"Create role success: {name}")
        flash("角色创建成功")
    else:
        app.HBlogFlask.print_sys_opt_success_log(f"Create role fail: {name}")
        flash("角色创建失败")
    return redirect(url_for("auth.role_page"))


@auth.route('/role/delete', methods=['POST'])
@login_required
@app.form_required(DeleteRoleForm, "delete role")
@app.role_required("ConfigureSystem", "delete role")
def role_delete_page():
    form: DeleteRoleForm = g.form
    if User.delete_role(form.name.data):
        app.HBlogFlask.print_sys_opt_success_log(f"Delete role success: {form.name.data}")
        flash("角色删除成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log(f"Delete role fail: {form.name.data}")
        flash("角色删除失败")
    return redirect(url_for("auth.role_page"))


@auth.route('/role/set', methods=['POST'])
@login_required
@app.form_required(SetRoleForm, "assign user a role")
@app.role_required("ConfigureSystem", "assign user a role")
def role_set_page():
    form: SetRoleForm = g.form
    user = form.email_user
    if user.set_user_role(form.name.data):
        app.HBlogFlask.print_sys_opt_success_log(f"Role assign {form.email.data} -> {form.name.data}")
        flash("角色设置成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log(f"Role assign {form.email.data} -> {form.name.data}")
        flash("角色设置失败")
    return redirect(url_for("auth.role_page"))


@auth.context_processor
def inject_base():
    """ auth 默认模板变量 """
    return {"top_nav": ["", "", "", "", "", "active"]}
