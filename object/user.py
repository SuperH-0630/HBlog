from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous.exc import BadData
from collections import namedtuple

from configure import conf
from sql.user import (read_user,
                      check_role,
                      create_user,
                      get_role_name,
                      delete_user,
                      change_passwd_hash,
                      create_role,
                      delete_role,
                      set_user_role,
                      get_role_list,
                      role_authority)
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

    @property
    def id(self):
        return 0


class _User(UserMixin):
    user_tuple = namedtuple("User", "passwd role id")

    @staticmethod
    def create(email, passwd_hash):
        if create_user(email, passwd_hash) is not None:
            return User(email)
        return None

    @staticmethod
    def creat_token(email: str, passwd_hash: str):
        s = Serializer(conf["SECRET_KEY"])
        return s.dumps({"email": email, "passwd_hash": passwd_hash})

    @staticmethod
    def load_token(token: str):
        s = Serializer(conf["SECRET_KEY"])
        try:
            token = s.loads(token, max_age=3600)
            return token['email'], token['passwd_hash']
        except BadData:
            return None

    @staticmethod
    def get_passwd_hash(passwd: str):
        return generate_password_hash(passwd)

    @staticmethod
    def create_role(name: str, authority):
        return create_role(name, authority)

    @staticmethod
    def delete_role(role_id: int):
        return delete_role(role_id)

    @staticmethod
    def get_role_list():
        return get_role_list()


class User(_User):
    RoleAuthorize = role_authority

    def __init__(self, email):
        self.email = email

    def get_id(self):
        """Flask要求的方法"""
        return self.email

    @property
    def is_active(self):
        """Flask要求的属性, 表示用户是否激活(可登录), HGSSystem没有封禁用户系统, 所有用户都是被激活的"""
        return self.id != -1

    @property
    def is_authenticated(self):
        """Flask要求的属性, 表示登录的凭据是否正确, 这里检查是否能 load_user_by_id"""
        return self.is_active

    @property
    def star_email(self):
        if len(self.email) <= 4:
            return f"{self.email[0]}****"
        else:
            email = f"{self.email[0]}****{self.email[5:]}"
            return email

    @property
    def info(self):
        return User.user_tuple(*read_user(self.email))

    @property
    def passwd_hash(self):
        return self.info.passwd

    @property
    def role(self):
        return self.info.role

    @property
    def role_name(self):
        return get_role_name(self.info.role)

    @property
    def id(self):
        return self.info.id

    @property
    def count(self):
        msg = object.msg.Message.get_msg_count(self)
        comment = object.comment.Comment.get_user_comment_count(self)
        blog = object.blog.BlogArticle.get_blog_count(None, self)
        return msg, comment, blog

    def check_passwd(self, passwd: str):
        return check_password_hash(self.passwd_hash, passwd)

    def check_role(self, operate: str):
        return check_role(self.role, operate)

    def delete(self):
        return delete_user(self.id)

    def change_passwd(self, passwd):
        return change_passwd_hash(self.id, self.get_passwd_hash(passwd))

    def set_user_role(self, role_id: int):
        return set_user_role(role_id, self.id)
