from flask import Blueprint, render_template, current_app
import app

about_me = Blueprint("about_me", __name__)


@about_me.route('/')
def about_me_page():
    app.HBlogFlask.print_load_page_log("about me")
    hblog: app.Hblog = current_app
    return render_template("about_me/about_me.html", about_me=hblog.about_me)


@about_me.context_processor
def inject_base():
    """ about me 默认模板变量 """
    return {"top_nav": ["", "", "", "", "active", ""]}
