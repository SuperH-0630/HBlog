from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from configure import conf
from sql.user import read_user, check_role, get_user_email, add_user, get_role_name
import core.blog
import core.comment
import core.msg


class LoaderUserError(Exception):
    pass


class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        super(AnonymousUser, self).__init__()
        self.role = 3  # 默认角色
        self.email = ""  # 无邮箱
        self.passwd_hash = ""  # 无密码

    def check_role(self, operate: str):
        return check_role(self.role, operate)

    @staticmethod
    def get_user_id():
        return 0


def load_user_by_email(email: str) -> "User":
    user = read_user(email)
    if len(user) == 0:
        raise LoaderUserError
    passwd_hash = user[0]
    role = user[1]
    user_id = user[2]
    return User(email, passwd_hash, role, user_id)


class User(UserMixin):
    def __init__(self, email, passwd_hash, role, user_id):
        self.email = email
        self.passwd_hash = passwd_hash
        self.role = role
        if role is not None:
            self.role_name = get_role_name(role)
        else:
            self.role_name = None
        self.id = user_id

    def count_info(self):
        msg = core.msg.Message.get_msg_count(self)
        comment = core.comment.Comment.get_user_comment_count(self)
        blog = core.blog.BlogArticle.get_blog_count(None, self)
        return msg, comment, blog

    @property
    def s_email(self):
        if len(self.email) <= 4:
            return f"{self.email[0]}****"
        else:
            email = f"{self.email[0]}****{self.email[5:]}"
            return email

    @staticmethod
    def load_user_by_id(user_id):
        email = get_user_email(user_id)
        if email is None:
            raise LoaderUserError
        return load_user_by_email(email)

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
        return self.id

    @staticmethod
    def creat_token(email: str, passwd_hash: str):
        s = Serializer(conf["secret-key"], expires_in=3600)
        return s.dumps({"email": email, "passwd_hash": passwd_hash})

    @staticmethod
    def load_token(token: str):
        s = Serializer(conf["secret-key"], expires_in=3600)
        try:
            token = s.loads(token)
            return token['email'], token['passwd_hash']
        except Exception:
            return None

    @staticmethod
    def get_passwd_hash(passwd: str):
        return generate_password_hash(passwd)

    def check_passwd(self, passwd: str):
        return check_password_hash(self.passwd_hash, passwd)

    def check_role(self, operate: str):
        return check_role(self.role, operate)

    def create_user(self):
        return add_user(self.email, self.passwd_hash)
