import os
import sys

from flask import Flask, url_for, request, current_app, render_template, Response, jsonify
from flask_mail import Mail
from flask_login import LoginManager, current_user
from flask_moment import Moment
from flask.logging import default_handler
from typing import Optional, Union

import logging.handlers
import logging
from bs4 import BeautifulSoup

from configure import conf
from object.user import AnonymousUser, User
from app.cache import cache

if conf["DEBUG_PROFILE"]:
    from werkzeug.middleware.profiler import ProfilerMiddleware


class HBlogFlask(Flask):
    def __init__(self, import_name: str, *args, **kwargs):
        super(HBlogFlask, self).__init__(import_name, *args, **kwargs)
        self.about_me = ""
        self.update_configure()

        if conf["DEBUG_PROFILE"]:
            self.wsgi_app = ProfilerMiddleware(self.wsgi_app, sort_by=("cumtime",))

        self.login_manager = LoginManager()
        self.login_manager.init_app(self)
        self.login_manager.anonymous_user = AnonymousUser  # 设置未登录的匿名对象
        self.login_manager.login_view = "auth.login_page"

        self.mail = Mail(self)
        self.moment = Moment(self)
        self.cache = cache
        self.cache.init_app(self)

        self.logger.removeHandler(default_handler)
        self.logger.setLevel(conf["LOG_LEVEL"])
        self.logger.propagate = False
        if len(conf["LOG_HOME"]) > 0:
            handle = logging.handlers.TimedRotatingFileHandler(
                os.path.join(conf["LOG_HOME"], f"flask.log"), backupCount=10)
            handle.setFormatter(logging.Formatter(conf["LOG_FORMAT"]))
            self.logger.addHandler(handle)
        if conf["LOG_STDERR"]:
            handle = logging.StreamHandler(sys.stderr)
            handle.setFormatter(logging.Formatter(conf["LOG_FORMAT"]))
            self.logger.addHandler(handle)

        @self.login_manager.user_loader
        def user_loader(email: str):
            user = User(email)
            if user.info.id == -1:
                return None
            return user

        res = []
        for i in [400, 401, 403, 404, 405, 408, 410, 413, 414, 423, 500, 501, 502]:
            def create_error_handle(status):
                def error_handle(e):
                    self.print_load_page_log(status)
                    if "/api" in request.base_url:
                        rsp = jsonify({"status": status, "error": str(e)})
                        rsp.status_code = status
                        return rsp
                    data = render_template('error.html', error_code=status, error_info=e)
                    return Response(response=data, status=status)
                return error_handle

            self.errorhandler(i)(create_error_handle(i))

    def register_all_blueprint(self):
        import app.index as index
        import app.archive as archive
        import app.docx as docx
        import app.msg as msg
        import app.oss as oss
        import app.auth as auth
        import app.about_me as about_me
        import app.api as api

        self.register_blueprint(index.index, url_prefix="/")
        self.register_blueprint(archive.archive, url_prefix="/archive")
        self.register_blueprint(docx.docx, url_prefix="/docx")
        self.register_blueprint(msg.msg, url_prefix="/msg")
        self.register_blueprint(auth.auth, url_prefix="/auth")
        self.register_blueprint(about_me.about_me, url_prefix="/about")
        self.register_blueprint(oss.oss, url_prefix="/oss")
        self.register_blueprint(api.api, url_prefix="/api")

    def update_configure(self):
        """ 更新配置 """
        self.config.update(conf)
        about_me_page = conf["ABOUT_ME_PAGE"]
        if len(about_me_page) > 0 and os.path.exists(about_me_page):
            with open(about_me_page, "r", encoding='utf-8') as f:
                bs = BeautifulSoup(f.read(), "html.parser")
            self.about_me = str(bs.find("body").find("div", class_="about-me"))  # 提取about-me部分的内容

    @staticmethod
    def get_max_page(count: int, count_page: int):
        """ 计算页码数 (共计count个元素, 每页count_page个元素) """
        return (count // count_page) + (0 if count % count_page == 0 else 1)

    @staticmethod
    def get_page(url, page: int, count: int):
        """ 计算页码的按钮 """
        if count <= 9:
            page_list = [[i + 1, url_for(url, page=i + 1)] for i in range(count)]
        elif page <= 5:
            """
            [1][2][3][4][5][6][...][count - 1][count]
            """
            page_list = [[i + 1, url_for(url, page=i + 1)] for i in range(6)]
            page_list += [None, [count - 1, url_for(url, page=count - 1)], [count, url_for(url, page=count)]]
        elif page >= count - 5:
            """
            [1][2][...][count - 5][count - 4][count - 3][count - 2][count - 1][count]
            """
            page_list: Optional[list] = [[1, url_for(url, page=1)], [2, url_for(url, page=2)], None]
            page_list += [[count - 5 + i, url_for(url, page=count - 5 + i)] for i in range(6)]
        else:
            """
            [1][2][...][page - 2][page - 1][page][page + 1][page + 2][...][count - 1][count]
            """
            page_list: Optional[list] = [[1, url_for(url, page=1)], [2, url_for(url, page=2)], None]
            page_list += [[page - 2 + i, url_for(url, page=page - 2 + i)] for i in range(5)]
            page_list += [None, [count - 1, url_for(url, page=count - 1)], [count, url_for(url, page=count)]]
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
