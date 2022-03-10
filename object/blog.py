from typing import Optional

from sql.base import DBBit
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
                      get_user_user_count)
from sql.archive import add_blog_to_archive, sub_blog_from_archive
import object.user
import object.archive
import object.comment


class LoadBlogError(Exception):
    pass


def load_blog_by_id(blog_id) -> "Optional[BlogArticle]":
    blog_id = blog_id
    blog = read_blog(blog_id)
    if len(blog) == 0:
        return None

    auth = object.user.load_user_by_id(blog[0])
    if auth is None:
        return None

    title = blog[1]
    subtitle = blog[2]
    content = blog[3]
    update_time = blog[4]
    create_time = blog[5]
    top = blog[6] == DBBit.BIT_1
    comment = object.comment.load_comment_list(blog_id)
    archive = object.archive.Archive.get_blog_archive(blog_id)
    return BlogArticle(blog_id, auth, title, subtitle, content, update_time, create_time, top, comment, archive)


class BlogArticle:
    def __init__(self, blog_id, auth, title, subtitle, content, update_time=None, create_time=None, top=False,
                 comment=None, archive=None):
        self.blog_id = blog_id
        self.user = auth
        self.title = title
        self.subtitle = subtitle
        self.content = content
        self.update_time = update_time
        self.create_time = create_time
        self.top = top
        self.comment = [] if comment is None else comment
        self.archive = [] if archive is None else archive

    @staticmethod
    def get_blog_list(archive_id=None, limit=None, offset=None, not_top=False):
        if archive_id is None:
            if not_top:
                return get_blog_list_not_top(limit=limit, offset=offset)
            return get_blog_list(limit=limit, offset=offset)
        return get_archive_blog_list(archive_id, limit=limit, offset=offset)

    @staticmethod
    def get_blog_count(archive_id=None, auth=None):
        if archive_id is None:
            return get_blog_count()
        if auth is None:
            return get_archive_blog_count(archive_id)
        return get_user_user_count(auth.get_user_id())

    def create(self):
        if self.blog_id is not None:  # 只有 blog_id为None时才使用
            return False
        return create_blog(self.user.get_user_id(), self.title, self.subtitle, self.content, self.archive)

    def delete(self):
        return delete_blog(self.blog_id)

    def update(self, content: str):
        if update_blog(self.blog_id, content):
            self.content = content
            return True
        return False

    def set_top(self, top: bool):
        set_blog_top(self.blog_id, top)

    def add_to_archive(self, archive_id: int):
        return add_blog_to_archive(self.blog_id, archive_id)

    def sub_from_archive(self, archive_id: int):
        return sub_blog_from_archive(self.blog_id, archive_id)
