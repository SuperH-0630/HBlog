from sql.comment import read_comment, create_comment, get_user_comment_count, delete_comment
import object.user

from typing import Optional


def load_comment_list(blog_id: int):
    comment_list = read_comment(blog_id)
    ret = []
    for comment in comment_list:
        ret.append(Comment(comment[0], blog_id, object.user.User(comment[2], None, None, comment[1]), comment[3], comment[4]))
    return ret


class Comment:
    def __init__(self, comment_id,
                 blog_id: Optional[int],
                 auth: "Optional[object.user.User]",
                 context: Optional[str], update_time=None):
        self.comment_id = comment_id
        self.blog_id = blog_id
        self.auth = auth
        self.context = context
        self.update_time = update_time

    @staticmethod
    def get_user_comment_count(auth: "object.user"):
        return get_user_comment_count(auth.get_user_id())

    def create(self):
        return create_comment(self.blog_id, self.auth.get_user_id(), self.context)

    def delete(self):
        return delete_comment(self.comment_id)
