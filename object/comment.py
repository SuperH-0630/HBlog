from collections import namedtuple
from datetime import datetime

from sql.comment import read_comment_list, create_comment, get_user_comment_count, delete_comment, read_comment
import object.user
import object.blog


def load_comment_list(blog_id: int):
    ret = []
    for i in read_comment_list(blog_id):
        ret.append(Comment(i))
    return ret


class _Comment:
    comment_tuple = namedtuple("Comment", "blog email content update_time")

    @staticmethod
    def get_user_comment_count(auth: "object.user"):
        return get_user_comment_count(auth.id)

    @staticmethod
    def create(blog: "object.blog.BlogArticle", auth: "object.user.User", content):
        return create_comment(blog.id, auth.id, content)


class Comment(_Comment):
    def __init__(self, comment_id):
        self.id = comment_id

    @property
    def info(self):
        return Comment.comment_tuple(*read_comment(self.id))

    @property
    def blog(self):
        return object.blog.BlogArticle(self.info.blog)

    @property
    def auth(self):
        return object.user.User(self.info.email)

    @property
    def content(self):
        return self.info.content

    @property
    def update_time(self):
        return datetime.utcfromtimestamp(datetime.timestamp(self.info.update_time))

    def is_delete(self):
        return not self.auth.is_authenticated and self.blog.is_delete  and len(self.content) != 0

    def delete(self):
        return delete_comment(self.id)
