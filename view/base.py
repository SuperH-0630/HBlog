from flask import Flask, url_for
from flask_mail import Mail
from flask_login import LoginManager
from typing import Optional

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
