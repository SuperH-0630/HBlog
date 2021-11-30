from sql.comment import read_comment, create_comment, get_user_comment_count
import core.user


def load_comment_list(blog_id: int):
    comment_list = read_comment(blog_id)
    ret = []
    for comment in comment_list:
        ret.append(Comment(comment[0], blog_id, core.user.User(comment[2], None, None, comment[1]), comment[3], comment[4]))
    return ret


class Comment:
    def __init__(self, comment_id, blog_id: int, auth: "core.user.User", context: str, update_time=None):
        self.comment_id = comment_id
        self.blog_id = blog_id
        self.auth = auth
        self.context = context
        self.update_time = update_time

    @staticmethod
    def get_user_comment_count(auth: "core.user"):
        return get_user_comment_count(auth.get_user_id())

    def create_comment(self):
        return create_comment(self.blog_id, self.auth.get_user_id(), self.context)
