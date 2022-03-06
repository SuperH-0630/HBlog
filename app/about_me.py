from flask import Blueprint, render_template
import app

about_me = Blueprint("about_me", __name__)


@about_me.route('/')
def about_me_page():
    app.HBlogFlask.print_load_page_log("about me")
    return render_template("about_me/about_me.html")


@about_me.context_processor
def inject_base():
    return {"top_nav": ["", "", "", "", "active", ""]}
