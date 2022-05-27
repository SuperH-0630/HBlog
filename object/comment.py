from sql.comment import read_comment_list, create_comment, get_user_comment_count, delete_comment, read_comment
import object.user
import object.blog


def load_comment_list(blog_id: int):
    ret = []
    for i in read_comment_list(blog_id):
        ret.append(Comment(i))
    return ret


class _Comment:
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
        return read_comment(self.id)

    @property
    def blog(self):
        return object.blog.BlogArticle(self.info[0])

    @property
    def auth(self):
        return object.user.User(self.info[1])

    @property
    def content(self):
        return self.info[2]

    @property
    def update_time(self):
        return self.info[3]

    def is_delete(self):
        return not self.auth.is_authenticated and self.blog.is_delete  and len(self.content) != 0

    def delete(self):
        return delete_comment(self.id)
