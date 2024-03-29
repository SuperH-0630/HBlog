from flask import Blueprint, render_template, request
from flask_login import current_user

from configure import conf
import app
from object.blog import BlogArticle
from object.msg import Message
from sql.statistics import get_hello_click, add_hello_click, get_home_click, add_home_click

index = Blueprint("base", __name__)


@index.route('/')
@app.cache.cached(timeout=conf["VIEW_CACHE_EXPIRE"])
def hello_page():
    app.HBlogFlask.print_load_page_log(f"hello")
    add_hello_click()
    return render_template("index/hello.html")


@index.route('/home')
def index_page():
    blog_list = BlogArticle.get_blog_list(limit=5, offset=0, not_top=True)
    msg_list = Message.get_message_list(limit=6, offset=0, show_secret=False)
    app.HBlogFlask.print_load_page_log(f"index")
    add_home_click()
    return render_template("index/index.html",
                           blog_list=blog_list,
                           msg_list=msg_list,
                           show_email=current_user.check_role("ReadUserInfo"),
                           hello_clicks=get_hello_click(),
                           home_clicks=get_home_click())


@index.context_processor
@app.cache.cached(timeout=conf["CACHE_EXPIRE"], key_prefix="inject_base:index")
def inject_base():
    """ index默认模板变量, 覆盖app变量 """
    return {"top_nav": ["active", "", "", "", "", ""]}


def get_icp():
    for i in conf["ICP"]:
        if i in request.host:
            return conf["ICP"][i]


def get_gongan():
    for i in conf["GONG_AN"]:
        if i in request.host:
            return conf["GONG_AN"][i]


@index.app_context_processor
@app.cache.cached(timeout=conf["CACHE_EXPIRE"], key_prefix="inject_base")
def inject_base():
    """ app默认模板变量 """
    return {"blog_name": conf['BLOG_NAME'],
            "top_nav": ["", "", "", "", "", ""],
            "blog_describe": conf['BLOG_DESCRIBE'],
            "conf": conf,
            "get_icp": get_icp,
            "get_gongan": get_gongan}
