from typing import Optional

from sql.msg import read_msg_list, get_msg_count, create_msg, read_msg, get_user_msg_count, delete_msg
import object.user


def load_message_list(limit: Optional[int] = None, offset: Optional[int] = None, show_secret: bool = False):
    ret = []
    for i in read_msg_list(limit=limit, offset=offset, show_secret=show_secret):
        ret.append(Message(i))
    return ret


class _Message:
    @staticmethod
    def get_msg_count(auth: "object.user" = None):
        if auth is None:
            return get_msg_count()
        return get_user_msg_count(auth.id)

    @staticmethod
    def create(auth: "object.user.User", content, secret: bool = False):
        ret = create_msg(auth.id, content, secret)
        if ret is not None:
            return Message(ret)
        return None


class Message(_Message):
    def __init__(self, msg_id):
        self.id = msg_id

    @property
    def info(self):
        return read_msg(self.id)

    @property
    def auth(self):
        return object.user.User(self.info[0])

    @property
    def content(self):
        return self.info[1]

    @property
    def update_time(self):
        return self.info[2]

    @property
    def secret(self):
        return self.info[3]

    @property
    def is_delete(self):
        return not self.auth.is_authenticated and len(self.content) != 0

    def delete(self):
        return delete_msg(self.id)
