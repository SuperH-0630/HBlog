from sql.comment import get_comment_list, write_comment, get_user_comment_count
import core.user


class LoadCommentError(Exception):
    pass


def load_comment_list(blog_id: int):
    comment_list = get_comment_list(blog_id)
    ret = []
    for comment in comment_list:
        ret.append(Comment(blog_id, core.user.User(comment[1], None, None, comment[0]), comment[2], comment[3]))
    return ret


class Comment:
    def __init__(self, blog_id: int, auth: "core.user.User", context: str, update_time=None):
        self.blog_id = blog_id
        self.auth = auth
        self.context = context
        self.update_time = update_time

    @staticmethod
    def get_user_comment_count(auth: "core.user"):
        return get_user_comment_count(auth.get_user_id())

    def create_comment(self):
        return write_comment(self.blog_id, self.auth.get_user_id(), self.context)
