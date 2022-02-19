from flask import Flask, Blueprint, render_template
from typing import Optional
from flask_login import current_user

from configure import conf
from view.base import App
from core.blog import BlogArticle
from core.msg import load_message_list

index = Blueprint("base", __name__)
app: Optional[Flask] = None


@index.route('/')
def hello_page():
    IndexApp.print_load_page_log(f"hello")
    return render_template("index/hello.html")


@index.route('/index')
def index_page():
    blog_list = BlogArticle.get_blog_list(limit=5, offset=0, not_top=True)
    msg_list = load_message_list(limit=6, offset=0, show_secret=False)
    IndexApp.print_load_page_log(f"index")
    return render_template("index/index.html",
                           blog_list=blog_list,
                           msg_list=msg_list,
                           show_email=current_user.check_role("ReadUserInfo"))


@index.app_errorhandler(404)
def error_404(e):
    IndexApp.print_load_page_log(f"404")
    return render_template("index/error.html", error_code="404", error_info=f"你似乎来到一片荒漠：{e}"), 404


@index.app_errorhandler(405)
def error_405(e):
    IndexApp.print_load_page_log(f"405")
    return render_template("index/error.html", error_code="404", error_info=f"请求错误：{e}"), 405


@index.app_errorhandler(403)
def error_403(e):
    IndexApp.print_load_page_log(f"403")
    return render_template("index/error.html", error_code="404", error_info=f"权限不足：{e}"), 403


@index.app_errorhandler(500)
def error_500(e):
    IndexApp.print_load_page_log(f"500")
    return render_template("index/error.html", error_code="404", error_info=f"服务器出问题啦：{e}"), 500


@index.context_processor
def inject_base():
    return {"top_nav": ["active", "", "", "", "", ""]}


@index.app_context_processor
def inject_base():
    return {"blog_name": conf['blog-name'],
            "top_nav": ["", "", "", "", "", ""],
            "blog_describe": conf['blog-describe'],
            "conf": conf}


class IndexApp(App):
    def __init__(self, import_name):
        super(IndexApp, self).__init__(import_name)

        global app
        app = self._app
        app.register_blueprint(index, url_prefix="/")

