from view.index import IndexApp
from view.docx import DocxApp
from view.archive import ArchiveApp
from view.msg import MsgApp
from view.about_me import AboutMeApp
from view.auth import AuthApp


class WebApp(IndexApp, DocxApp, ArchiveApp, MsgApp, AboutMeApp, AuthApp):
    def __init__(self, import_name):
        super(WebApp, self).__init__(import_name)
