from typing import Optional
from collections import namedtuple
from datetime import datetime

from sql.msg import read_msg_list, get_msg_count, create_msg, read_msg, get_user_msg_count, delete_msg
import object.user


class _Message:
    message_tuple = namedtuple("Message", "email content update_time secret")

    @staticmethod
    def get_message_list(limit: Optional[int] = None, offset: Optional[int] = None, show_secret: bool = False):
        ret = []
        for i in read_msg_list(limit=limit, offset=offset, show_secret=show_secret):
            ret.append(Message(i))
        return ret

    @staticmethod
    def get_msg_count(auth: "object.user.User" = None):
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
        return Message.message_tuple(*read_msg(self.id))

    @property
    def auth(self):
        return object.user.User(self.info.email)

    @property
    def content(self):
        return self.info.content

    @property
    def update_time(self):
        return datetime.utcfromtimestamp(datetime.timestamp(self.info.update_time))

    @property
    def secret(self):
        return self.info.secret

    @property
    def is_delete(self):
        return not self.auth.is_authenticated and len(self.content) != 0

    def delete(self):
        return delete_msg(self.id)
