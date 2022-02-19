from flask import Flask, Blueprint, render_template, current_app, request
from typing import Optional

from view.base import App


about_me = Blueprint("about_me", __name__)
app: Optional[Flask] = None


@about_me.route('/')
def about_me_page():
    AboutMeApp.print_load_page_log("about me")
    return render_template("about_me/about_me.html")


@about_me.context_processor
def inject_base():
    return {"top_nav": ["", "", "", "", "active", ""]}


class AboutMeApp(App):
    def __init__(self, import_name):
        super(AboutMeApp, self).__init__(import_name)

        global app
        app = self._app
        app.register_blueprint(about_me, url_prefix="/about-me")
