from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous.exc import BadData
from typing import Optional

from configure import conf
from sql.user import (read_user,
                      check_role,
                      get_user_email,
                      create_user,
                      get_role_name,
                      delete_user,
                      change_passwd_hash,
                      create_role,
                      delete_role,
                      set_user_role)
import object.blog
import object.comment
import object.msg


class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        super(AnonymousUser, self).__init__()
        self.role = 4  # 默认角色
        self.email = ""  # 无邮箱
        self.passwd_hash = ""  # 无密码

    def check_role(self, operate: str):
        return check_role(self.role, operate)

    @staticmethod
    def get_user_id():
        return 0


def load_user_by_email(email: str) -> "Optional[User]":
    user = read_user(email)
    if len(user) == 0:
        return None
    passwd_hash = user[0]
    role = user[1]
    user_id = user[2]
    return User(email, passwd_hash, role, user_id)


def load_user_by_id(user_id):
    email = get_user_email(user_id)
    if email is None:
        return None
    return load_user_by_email(email)


class User(UserMixin):
    def __init__(self, email, passwd_hash, role, user_id):
        self.email = email
        self.passwd_hash = passwd_hash
        self.role = role
        if role is not None:
            self.role_name = get_role_name(role)
        else:
            self.role_name = None
        self.user_id = user_id

    def count_info(self):
        msg = object.msg.Message.get_msg_count(self)
        comment = object.comment.Comment.get_user_comment_count(self)
        blog = object.blog.BlogArticle.get_blog_count(None, self)
        return msg, comment, blog

    @property
    def s_email(self):
        if len(self.email) <= 4:
            return f"{self.email[0]}****"
        else:
            email = f"{self.email[0]}****{self.email[5:]}"
            return email

    @property
    def comment_count(self):
        return 0

    @property
    def blog_count(self):
        return 0

    @property
    def msg_count(self):
        return 0

    @property
    def is_active(self):
        """Flask要求的属性, 表示用户是否激活(可登录), HGSSystem没有封禁用户系统, 所有用户都是被激活的"""
        return True

    @property
    def is_authenticated(self):
        """Flask要求的属性, 表示登录的凭据是否正确, 这里检查是否能 load_user_by_id"""
        return True

    def get_id(self):
        """Flask要求的方法"""
        return self.email

    def get_user_id(self):
        return self.user_id

    @staticmethod
    def creat_token(email: str, passwd_hash: str):
        s = Serializer(conf["secret-key"])
        return s.dumps({"email": email, "passwd_hash": passwd_hash})

    @staticmethod
    def load_token(token: str):
        s = Serializer(conf["secret-key"])
        try:
            token = s.loads(token, max_age=3600)
            return token['email'], token['passwd_hash']
        except BadData:
            return None

    @staticmethod
    def get_passwd_hash(passwd: str):
        return generate_password_hash(passwd)

    def check_passwd(self, passwd: str):
        return check_password_hash(self.passwd_hash, passwd)

    def check_role(self, operate: str):
        return check_role(self.role, operate)

    def create(self):
        return create_user(self.email, self.passwd_hash)

    def delete(self):
        return delete_user(self.user_id)

    def change_passwd(self, passwd):
        return change_passwd_hash(self.user_id, self.get_passwd_hash(passwd))

    @staticmethod
    def create_role(name: str, authority):
        return create_role(name, authority)

    @staticmethod
    def delete_role(name: str):
        return delete_role(name)

    def set_user_role(self, name: str):
        return set_user_role(name, self.user_id)
