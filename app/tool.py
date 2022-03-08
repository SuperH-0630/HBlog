from functools import wraps
from flask import abort
from flask_login import current_user
from flask_wtf import FlaskForm
from typing import ClassVar
import app


def role_required(role: str, opt: str):
    def required(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            if not current_user.check_role(role):  # 检查相应的权限
                app.HBlogFlask.print_user_not_allow_opt_log(opt)
                return abort(403)
            return func(*args, **kwargs)
        return new_func
    return required


def form_required(form: ClassVar[FlaskForm], opt: str):
    def required(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            f = form()
            if not f.validate_on_submit():
                app.HBlogFlask.print_form_error_log(opt)
                return abort(404)
            return func(*args, **kwargs, form=f)
        return new_func
    return required