from typing import List
from collections import namedtuple
from datetime import datetime

from sql.blog import (get_blog_list,
                      get_blog_count,
                      get_archive_blog_list,
                      get_archive_blog_count,
                      get_blog_list_not_top,
                      read_blog,
                      update_blog,
                      create_blog,
                      delete_blog,
                      set_blog_top,
                      get_user_blog_count)
from sql.statistics import get_blog_click
from sql.archive import add_blog_to_archive, sub_blog_from_archive
from sql.user import get_user_email
from sql.base import DBBit
import object.user
import object.archive
import object.comment


class LoadBlogError(Exception):
    pass


class _BlogArticle:
    article_tuple = namedtuple("Article", "auth title subtitle content update_time create_time top")

    @staticmethod
    def get_blog_list(archive_id=None, limit=None, offset=None, not_top=False):
        if archive_id is None:
            if not_top:
                res = get_blog_list_not_top(limit=limit, offset=offset)
            else:
                res = get_blog_list(limit=limit, offset=offset)
        else:
            res = get_archive_blog_list(archive_id, limit=limit, offset=offset)

        ret = []
        for i in res:
            ret.append(BlogArticle(i))
        return ret

    @staticmethod
    def get_blog_count(archive_id=None, auth=None):
        if archive_id is None and auth is None:
            return get_blog_count()
        if auth is None:
            return get_archive_blog_count(archive_id)
        return get_user_blog_count(auth.id)

    @staticmethod
    def create(title, subtitle, content, archive: "List[object.archive.Archive]", user: "object.user.User"):
        return create_blog(user.id, title, subtitle, content, archive)


class BlogArticle(_BlogArticle):
    def __init__(self, blog_id):
        self.id = blog_id

    @property
    def info(self):
        return BlogArticle.article_tuple(*read_blog(self.id))

    @property
    def user(self):
        return object.user.User(get_user_email(self.info.auth))

    @property
    def title(self):
        return self.info.title

    @property
    def subtitle(self):
        return self.info.subtitle

    @property
    def content(self):
        return self.info.content

    @property
    def update_time(self):
        return datetime.utcfromtimestamp(datetime.timestamp(self.info.update_time))

    @property
    def create_time(self):
        return datetime.utcfromtimestamp(datetime.timestamp(self.info.create_time))

    @property
    def clicks(self):
        return get_blog_click(self.id)

    @property
    def top(self):
        return self.info.top

    @top.setter
    def top(self, top: bool):
        set_blog_top(self.id, top)

    @property
    def comment(self):
        return object.comment.load_comment_list(self.id)

    @property
    def archive(self):
        return object.archive.Archive.get_blog_archive(self.id)

    @property
    def is_delete(self):
        return not self.user.is_authenticated and len(self.content) != 0

    def delete(self):
        return delete_blog(self.id)

    def update(self, content: str):
        if update_blog(self.id, content):
            return True
        return False

    def add_to_archive(self, archive_id: int):
        return add_blog_to_archive(self.id, archive_id)

    def sub_from_archive(self, archive_id: int):
        return sub_blog_from_archive(self.id, archive_id)
