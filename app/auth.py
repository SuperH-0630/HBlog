from flask import Blueprint, render_template, redirect, flash, url_for, request, abort, current_app, g
from flask_login import login_required, login_user, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo

import app
from object.user import User, load_user_by_email
from send_email import send_msg

auth = Blueprint("auth", __name__)


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
            raise ValidationError("邮箱已被注册")


class ChangePasswdForm(FlaskForm):
    old_passwd = PasswordField("旧密码", validators=[DataRequired()])
    passwd = PasswordField("新密码", validators=[DataRequired(),
                                              EqualTo("passwd_again", message="两次输入密码不相同"),
                                              Length(8, 32)])
    passwd_again = PasswordField("重复密码", validators=[DataRequired()])
    submit = SubmitField("修改密码")


class DeleteUserForm(FlaskForm):
    email = StringField("邮箱", validators=[DataRequired(), Length(1, 32)])
    submit = SubmitField("删除用户")

    def validate_email(self, field):
        if load_user_by_email(field.data) is None:
            raise ValidationError("邮箱用户不存在")


class CreateRoleForm(FlaskForm):
    name = StringField("角色名称", validators=[DataRequired(), Length(1, 20)])
    authority = StringField("权限", validators=[Length(0, 100)])
    submit = SubmitField("创建角色")


class DeleteRoleForm(FlaskForm):
    name = StringField("角色名称", validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField("删除角色")


class SetRoleForm(FlaskForm):
    email = StringField("邮箱", validators=[DataRequired(), Length(1, 32)])
    name = StringField("角色名称", validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField("设置角色")


@auth.route('/yours')
@login_required
def yours_page():
    msg_count, comment_count, blog_count = current_user.count_info()
    app.HBlogFlask.print_load_page_log("user info")
    return render_template("auth/yours.html", msg_count=msg_count, comment_count=comment_count, blog_count=blog_count)


@auth.route('/login', methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        app.HBlogFlask.print_user_not_allow_opt_log("login")
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
            app.HBlogFlask.print_user_opt_success_log(f"login {form.email.data}")
            return redirect(next_page)
        flash("账号或密码错误")
        app.HBlogFlask.print_user_opt_fail_log(f"login {form.email.data}")
        return redirect(url_for("auth.login_page"))
    app.HBlogFlask.print_load_page_log("user login")
    return render_template("auth/login.html", form=form)


@auth.route('/register', methods=["GET", "POST"])
def register_page():
    if current_user.is_authenticated:
        app.HBlogFlask.print_user_not_allow_opt_log("register")
        return redirect(url_for("auth.yours_page"))

    form = RegisterForm()
    if form.validate_on_submit():
        token = User.creat_token(form.email.data, form.passwd.data)
        register_url = url_for("auth.confirm_page", token=token, _external=True)
        hblog: app.Hblog = current_app
        send_msg("注册确认", hblog.mail, form.email.data, "register", register_url=register_url)
        flash("注册提交成功, 请进入邮箱点击确认注册链接")
        app.HBlogFlask.print_import_user_opt_success_log(f"register {form.email.data}")
        return redirect(url_for("base.index_page"))
    app.HBlogFlask.print_load_page_log("user register")
    return render_template("auth/register.html", RegisterForm=form)


@auth.route('/confirm')
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

    if load_user_by_email(token[0]) is not None:
        app.HBlogFlask.print_user_opt_fail_log(f"Confirm (bad token)")
        abort(404)
        return

    User(token[0], token[1], None, None).create()
    current_app.logger.info(f"{token[0]} confirm success")
    app.HBlogFlask.print_import_user_opt_success_log(f"confirm {token[0]}")
    flash(f"用户{token[0]}认证完成")
    return redirect(url_for("base.index_page"))


@auth.route('/logout')
@login_required
def logout_page():
    app.HBlogFlask.print_import_user_opt_success_log(f"logout")
    logout_user()
    flash("退出登录成功")
    return redirect(url_for("base.index_page"))


@auth.route('/passwd', methods=['GET', 'POST'])
@login_required
def change_passwd_page():
    form = ChangePasswdForm()
    if form.validate_on_submit():
        if not current_user.check_passwd(form.old_passwd.data):
            app.HBlogFlask.print_user_opt_fail_log("change passwd (old passwd error)")
            flash("旧密码错误")
            return redirect(url_for("auth.change_passwd_page"))
        if current_user.change_passwd(form.passwd.data):
            app.HBlogFlask.print_user_opt_success_log(f"change passwd")
            flash("密码修改成功")
        else:
            app.HBlogFlask.print_user_opt_error_log(f"change passwd")
            flash("密码修改失败")
        return redirect(url_for("auth.yours_page"))
    app.HBlogFlask.print_load_page_log("user change passwd")
    return render_template("auth/passwd.html", ChangePasswdForm=form)


@auth.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_user_page():
    if not current_user.check_role("DeleteUser"):
        app.HBlogFlask.print_user_not_allow_opt_log("delete user")
        abort(403)
        return

    form = DeleteUserForm()
    if form.validate_on_submit():
        user = load_user_by_email(form.email.data)
        if user is None:
            app.HBlogFlask.print_sys_opt_fail_log(f"delete user {form.email.data}")
            abort(404)
            return

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
def role_page():
    if not current_user.check_role("ConfigureSystem"):
        app.HBlogFlask.print_user_not_allow_opt_log("load role setting")
        abort(403)
        return

    app.HBlogFlask.print_load_page_log("role setting")
    return render_template("auth/role.html",
                           CreateRoleForm=CreateRoleForm(),
                           DeleteRoleForm=DeleteRoleForm(),
                           SetRoleForm=SetRoleForm())


@auth.route('/role-create', methods=['POST'])
@login_required
def role_create_page():
    form = CreateRoleForm()
    if form.validate_on_submit():
        if not current_user.check_role("ConfigureSystem"):
            app.HBlogFlask.print_user_not_allow_opt_log("create role")
            abort(403)
            return

        if User.create_role(form.name.data, form.authority.data.replace(" ", "").split(";")):
            app.HBlogFlask.print_sys_opt_success_log(f"Create role success: {form.name.data}")
            flash("角色创建成功")
        else:
            app.HBlogFlask.print_sys_opt_success_log(f"Create role fail: {form.name.data}")
            flash("角色创建失败")
        return redirect(url_for("auth.role_page"))

    abort(404)
    return


@auth.route('/role-delete', methods=['POST'])
@login_required
def role_delete_page():
    form = DeleteRoleForm()
    if form.validate_on_submit():
        if not current_user.check_role("ConfigureSystem"):
            app.HBlogFlask.print_user_not_allow_opt_log("delete role")
            abort(403)
            return

        if User.delete_role(form.name.data):
            app.HBlogFlask.print_sys_opt_success_log(f"Delete role success: {form.name.data}")
            flash("角色删除成功")
        else:
            app.HBlogFlask.print_sys_opt_fail_log(f"Delete role fail: {form.name.data}")
            flash("角色删除失败")
        return redirect(url_for("auth.role_page"))

    abort(404)
    return


@auth.route('/role-set', methods=['POST'])
@login_required
def role_set_page():
    form = SetRoleForm()
    if form.validate_on_submit():
        if not current_user.check_role("ConfigureSystem"):
            app.HBlogFlask.print_user_not_allow_opt_log("assign user a role")
            abort(403)
            return

        user = load_user_by_email(form.email.data)
        if user is not None:
            if user.set_user_role(form.name.data):
                app.HBlogFlask.print_sys_opt_success_log(f"Role assign {form.email.data} -> {form.name.data}")
                flash("角色设置成功")
            else:
                app.HBlogFlask.print_sys_opt_fail_log(f"Role assign {form.email.data} -> {form.name.data}")
                flash("角色设置失败")
        else:
            app.HBlogFlask.print_sys_opt_fail_log(f"Role assign (bad email) {form.email.data} -> {form.name.data}")
            flash("邮箱未注册")
        return redirect(url_for("auth.role_page"))

    abort(404)
    return


@auth.context_processor
def inject_base():
    return {"top_nav": ["", "", "", "", "", "active"]}
