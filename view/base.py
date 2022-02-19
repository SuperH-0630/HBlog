import os.path

from flask import Flask, url_for, request, current_app
from flask_mail import Mail
from flask_login import LoginManager, current_user
from typing import Optional

import sys
import logging.handlers
import logging
from configure import conf
from core.user import AnonymousUser


class App:
    def __init__(self, import_name: str):
        self._app = Flask(import_name)
        self._app.config["SECRET_KEY"] = conf['secret-key']

        self.login_manager = LoginManager()
        self.login_manager.init_app(self._app)
        self.login_manager.anonymous_user = AnonymousUser  # 设置未登录的匿名对象

        self._app.config["MAIL_SERVER"] = conf['email_server']
        self._app.config["MAIL_PORT"] = conf['email_port']
        self._app.config["MAIL_USE_TLS"] = conf['email_tls']
        self._app.config["MAIL_USE_SSL"] = conf['email_ssl']
        self._app.config["MAIL_USERNAME"] = conf['email_name']
        self._app.config["MAIL_PASSWORD"] = conf['email_passwd']

        self.mail = Mail(self._app)

        self._app.logger.setLevel(conf["log-level"])
        if conf["log-home"] is not None:
            handle = logging.handlers.TimedRotatingFileHandler(
                os.path.join(conf["log-home"], f"flask-{os.getpid()}.log"))
            handle.setFormatter(logging.Formatter(conf["log-format"]))
            self._app.logger.addHandler(handle)
        else:
            handle = logging.StreamHandler(sys.stderr)
            handle.setFormatter(logging.Formatter(conf["log-format"]))
            self._app.logger.addHandler(handle)

    def get_app(self) -> Flask:
        return self._app

    def run(self):
        self.run()

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
            f"[{request.method}] Load - '{page}' " + App.__get_log_request_info())

    @staticmethod
    def print_form_error_log(opt: str):
        current_app.logger.warning(
            f"[{request.method}] '{opt}' - Bad form " + App.__get_log_request_info())

    @staticmethod
    def print_sys_opt_fail_log(opt: str):
        current_app.logger.error(
            f"[{request.method}] System {opt} - fail " + App.__get_log_request_info())

    @staticmethod
    def print_sys_opt_success_log(opt: str):
        current_app.logger.warning(
            f"[{request.method}] System {opt} - success " + App.__get_log_request_info())

    @staticmethod
    def print_user_opt_fail_log(opt: str):
        current_app.logger.debug(
            f"[{request.method}] User {opt} - fail " + App.__get_log_request_info())

    @staticmethod
    def print_user_opt_success_log(opt: str):
        current_app.logger.debug(
            f"[{request.method}] User {opt} - success " + App.__get_log_request_info())

    @staticmethod
    def print_user_opt_error_log(opt: str):
        current_app.logger.warning(
            f"[{request.method}] User {opt} - system fail " + App.__get_log_request_info())

    @staticmethod
    def print_import_user_opt_success_log(opt: str):
        current_app.logger.info(
            f"[{request.method}] User {opt} - success " + App.__get_log_request_info())

    @staticmethod
    def print_user_not_allow_opt_log(opt: str):
        current_app.logger.info(
            f"[{request.method}] User '{opt}' - reject " + App.__get_log_request_info())
