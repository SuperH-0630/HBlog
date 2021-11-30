from typing import Optional

from sql.blog import (get_blog_list,
                      get_blog_count,
                      get_file_blog_list,
                      get_file_blog_count,
                      get_blog_list_not_top,
                      read_blog,
                      create_blog,
                      delete_blog,
                      get_user_user_count)
import core.user
import core.file
import core.comment


class LoadBlogError(Exception):
    pass


def load_blog_by_id(blog_id) -> "Optional[BlogArticle]":
    blog_id = blog_id
    blog = read_blog(blog_id)
    if len(blog) == 0:
        return None

    auth = core.user.load_user_by_id(blog[0])
    if auth is None:
        return None

    title = blog[1]
    subtitle = blog[2]
    context = blog[3]
    update_time = blog[6]
    top = blog[7]
    comment = core.comment.load_comment_list(blog_id)
    file = core.file.File.get_blog_file(blog_id)
    return BlogArticle(blog_id, auth, title, subtitle, context, update_time, top, comment, file)


class BlogArticle:
    def __init__(self, blog_id, auth, title, subtitle, context, update_time=None, top=False, comment=None, file=None):
        self.blog_id = blog_id
        self.user = auth
        self.title = title
        self.subtitle = subtitle
        self.context = context
        self.update_time = update_time
        self.top = top
        self.comment = [] if comment is None else comment
        self.file = [] if file is None else file

    @staticmethod
    def get_blog_list(file_id=None, limit=None, offset=None, not_top=False):
        if file_id is None:
            if not_top:
                return get_blog_list_not_top(limit=limit, offset=offset)
            return get_blog_list(limit=limit, offset=offset)
        return get_file_blog_list(file_id, limit=limit, offset=offset)

    @staticmethod
    def get_blog_count(file_id=None, auth=None):
        if file_id is None:
            return get_blog_count()
        if auth is None:
            return get_file_blog_count(file_id)
        return get_user_user_count(auth.get_user_id())

    def create(self):
        if self.blog_id is not None:  # 只有 blog_id为None时才使用
            return False
        return create_blog(self.user.get_user_id(), self.title, self.subtitle, self.context, self.file)

    def delete(self):
        return delete_blog(self.blog_id)
