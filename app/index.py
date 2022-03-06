from flask import Blueprint, render_template
from flask_login import current_user

from configure import conf
import app
from object.blog import BlogArticle
from object.msg import load_message_list

index = Blueprint("base", __name__)


@index.route('/')
def hello_page():
    app.HBlogFlask.print_load_page_log(f"hello")
    return render_template("index/hello.html")


@index.route('/index')
def index_page():
    blog_list = BlogArticle.get_blog_list(limit=5, offset=0, not_top=True)
    msg_list = load_message_list(limit=6, offset=0, show_secret=False)
    app.HBlogFlask.print_load_page_log(f"index")
    return render_template("index/index.html",
                           blog_list=blog_list,
                           msg_list=msg_list,
                           show_email=current_user.check_role("ReadUserInfo"))


@index.context_processor
def inject_base():
    return {"top_nav": ["active", "", "", "", "", ""]}


@index.app_context_processor
def inject_base():
    return {"blog_name": conf['BLOG_NAME'],
            "top_nav": ["", "", "", "", "", ""],
            "blog_describe": conf['BLOG_DESCRIBE'],
            "conf": conf}
