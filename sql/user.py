from sql import db
from sql.base import DBBit
import core.user


def get_user_email(user_id):
    cur = db.search(columns=["Email"], table="user", where=f"ID='{user_id}'")
    if cur is None or cur.rowcount == 0:
        return None
    return cur.fetchone()[0]


def read_user(email: str):
    cur = db.search(columns=["PasswdHash", "Role", "ID"], table="user", where=f"Email='{email}'")
    if cur is None or cur.rowcount == 0:
        return []
    assert cur.rowcount == 1
    return cur.fetchone()


def add_user(email: str, passwd: str):
    cur = db.search(columns=["count(Email)"], table="user")  # 统计个数
    passwd = core.user.User.get_passwd_hash(passwd)
    if cur is None or cur.rowcount == 0 or cur.fetchone()[0] == 0:
        db.insert(table='user', columns=['Email', 'PasswdHash', 'Role'], values=f"'{email}', '{passwd}', 1")  # 创建为管理员用户
    else:
        db.insert(table='user', columns=['Email', 'PasswdHash'], values=f"'{email}', '{passwd}'")


def get_role_name(role: int):
    cur = db.search(columns=["RoleName"], table="role", where=f"RoleID={role}")
    if cur is None or cur.rowcount == 0:
        return None
    return cur.fetchone()[0]


def check_role(role: int, operate: str):
    cur = db.search(columns=[operate], table="role", where=f"RoleID={role}")
    if cur is None or cur.rowcount == 0:
        return False
    return cur.fetchone()[0] == DBBit.BIT_1


def check_role_by_name(role: str, operate: str):
    cur = db.search(columns=[operate], table="role", where=f"RoleName='{role}")
    if cur is None or cur.rowcount == 0:
        return False
    return cur.fetchone()[0] == DBBit.BIT_1
