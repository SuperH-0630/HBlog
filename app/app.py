import os
import sys

from flask import Flask, url_for, request, current_app, g, render_template
from flask_mail import Mail
from flask_login import LoginManager, current_user
from flask.logging import default_handler
from typing import Optional, Union

import logging.handlers
import logging
from bs4 import BeautifulSoup

from configure import conf
from object.user import AnonymousUser, load_user_by_email

from .index import index
from .archive import archive
from .docx import docx
from .msg import msg
from .oss import oss
from .auth import auth
from .about_me import about_me


class HBlogFlask(Flask):
    def __init__(self, import_name: str, *args, **kwargs):
        super(HBlogFlask, self).__init__(import_name, *args, **kwargs)
        self.about_me = ""
        self.update_configure()

        self.register_blueprint(index, url_prefix="/")
        self.register_blueprint(archive, url_prefix="/archive")
        self.register_blueprint(docx, url_prefix="/docx")
        self.register_blueprint(msg, url_prefix="/msg")
        self.register_blueprint(auth, url_prefix="/auth")
        self.register_blueprint(about_me, url_prefix="/about")
        self.register_blueprint(oss, url_prefix="/oss")

        self.login_manager = LoginManager()
        self.login_manager.init_app(self)
        self.login_manager.anonymous_user = AnonymousUser  # 设置未登录的匿名对象
        self.login_manager.login_view = "auth.login_page"

        self.mail = Mail(self)

        self.logger.removeHandler(default_handler)
        self.logger.setLevel(conf["LOG_LEVEL"])
        self.logger.propagate = False
        if len(conf["LOG_HOME"]) > 0:
            handle = logging.handlers.TimedRotatingFileHandler(
                os.path.join(conf["LOG_HOME"], f"flask-.log"))
            handle.setFormatter(logging.Formatter(conf["LOG_FORMAT"]))
            self.logger.addHandler(handle)
        if conf["LOG_STDERR"]:
            handle = logging.StreamHandler(sys.stderr)
            handle.setFormatter(logging.Formatter(conf["LOG_FORMAT"]))
            self.logger.addHandler(handle)

        @self.login_manager.user_loader
        def user_loader(email: str):
            return load_user_by_email(email)

        func = {"render_template": render_template, "self": self}
        for i in [400, 401, 403, 404, 405, 408, 410, 413, 414, 423, 500, 501, 502]:
            exec(f"def error_{i}(e):\n"
                 f"\tself.print_load_page_log('{i}')\n"
                 f"\treturn render_template('error.html', error_code='{i}', error_info=e)", func)
            self.errorhandler(i)(func[f"error_{i}"])

    def update_configure(self):
        self.config.update(conf)
        about_me_page = conf["ABOUT_ME_PAGE"]
        if len(about_me_page) > 0 and os.path.exists(about_me_page):
            with open(about_me_page, "r", encoding='utf-8') as f:
                bs = BeautifulSoup(f.read(), "html.parser")
            self.about_me = str(bs.find("body").find("div", class_="about-me"))

    @staticmethod
    def get_max_page(count: int, count_page: int):
        return (count // count_page) + (0 if count % count_page == 0 else 1)

    @staticmethod
    def get_page(url, page: int, count: int):
        if count <= 9:
            page_list = [[f"{i + 1}", url_for(url, page=i + 1)] for i in range(count)]
        elif page <= 5:
            """
            [1][2][3][4][5][6][...][count - 1][count]
            """
            page_list = [[f"{i + 1}", url_for(url, page=i + 1)] for i in range(6)]

            page_list += [None,
                          [f"{count - 1}", url_for(url, page=count - 1)],
                          [f"{count}", url_for(url, page=count)]]
        elif page >= count - 5:
            """
            [1][2][...][count - 5][count - 4][count - 3][count - 2][count - 1][count]
            """
            page_list: Optional[list] = [["1", url_for(url, page=1)],
                                         ["2", url_for(url, page=2)],
                                         None]
            page_list += [[f"{count - 5 + i}", url_for(url, page=count - 5 + i), False] for i in range(6)]
        else:
            """
            [1][2][...][page - 2][page - 1][page][page + 1][page + 2][...][count - 1][count]
            """
            page_list: Optional[list] = [["1", url_for(url, page=1)],
                                         ["2", url_for(url, page=2)],
                                         None]
            page_list += [[f"{page - 2 + i}", url_for(url, page=page - 2 + i)] for i in range(5)]
            page_list += [None,
                          [f"{count - 1}", url_for(url, page=count - 1)],
                          [f"{count}", url_for(url, page=count)]]
        return page_list

    @staticmethod
    def __get_log_request_info():
        return (f"user: '{current_user.email}' "
                f"url: '{request.url}' blueprint: '{request.blueprint}' "
                f"args: {request.args} form: {request.form} "
                f"accept_encodings: '{request.accept_encodings}' "
                f"accept_charsets: '{request.accept_charsets}' "
                f"accept_mimetypes: '{request.accept_mimetypes}' "
                f"accept_languages: '{request.accept_languages}'")

    @staticmethod
    def print_load_page_log(page: str):
        current_app.logger.debug(
            f"[{request.method}] Load - '{page}' " + HBlogFlask.__get_log_request_info())

    @staticmethod
    def print_form_error_log(opt: str):
        current_app.logger.warning(
            f"[{request.method}] '{opt}' - Bad form " + HBlogFlask.__get_log_request_info())

    @staticmethod
    def print_sys_opt_fail_log(opt: str):
        current_app.logger.error(
            f"[{request.method}] System {opt} - fail " + HBlogFlask.__get_log_request_info())

    @staticmethod
    def print_sys_opt_success_log(opt: str):
        current_app.logger.warning(
            f"[{request.method}] System {opt} - success " + HBlogFlask.__get_log_request_info())

    @staticmethod
    def print_user_opt_fail_log(opt: str):
        current_app.logger.debug(
            f"[{request.method}] User {opt} - fail " + HBlogFlask.__get_log_request_info())

    @staticmethod
    def print_user_opt_success_log(opt: str):
        current_app.logger.debug(
            f"[{request.method}] User {opt} - success " + HBlogFlask.__get_log_request_info())

    @staticmethod
    def print_user_opt_error_log(opt: str):
        current_app.logger.warning(
            f"[{request.method}] User {opt} - system fail " + HBlogFlask.__get_log_request_info())

    @staticmethod
    def print_import_user_opt_success_log(opt: str):
        current_app.logger.info(
            f"[{request.method}] User {opt} - success " + HBlogFlask.__get_log_request_info())

    @staticmethod
    def print_user_not_allow_opt_log(opt: str):
        current_app.logger.info(
            f"[{request.method}] User '{opt}' - reject " + HBlogFlask.__get_log_request_info())


Hblog = Union[HBlogFlask, Flask]

