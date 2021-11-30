from typing import Optional

from sql.msg import read_msg, get_msg_count, create_msg, get_user_msg_count
import core.user


def load_message_list(limit: Optional[int] = None, offset: Optional[int] = None, show_secret: bool = False):
    msg = read_msg(limit=limit, offset=offset, show_secret=show_secret)
    ret = []
    for i in msg:
        ret.append(Message(i[0], core.user.User(i[2], None, None, i[1]), i[3], i[5], i[4]))
    return ret


class Message:
    def __init__(self, msg_id, auth: "core.user.User", context, secret, update_time):
        self.msg_id = msg_id
        self.auth = auth
        self.context = context
        self.secret = secret
        self.update_time = update_time

    @staticmethod
    def get_msg_count(auth: "core.user" = None):
        if auth is None:
            return get_msg_count()
        return get_user_msg_count(auth.get_user_id())

    def create_msg(self):
        return create_msg(self.auth.get_user_id(), self.context, self.secret)
