from sql import db
from sql.base import DBBit
import core.user


def read_user(email: str):
    """ 读取用户 """
    cur = db.search(columns=["PasswdHash", "Role", "ID"], table="user", where=f"Email='{email}'")
    if cur is None or cur.rowcount == 0:
        return []
    assert cur.rowcount == 1
    return cur.fetchone()


def create_user(email: str, passwd: str):
    """ 创建用户 """
    cur = db.search(columns=["count(Email)"], table="user")  # 统计个数
    passwd = core.user.User.get_passwd_hash(passwd)
    if cur is None or cur.rowcount == 0 or cur.fetchone()[0] == 0:
        db.insert(table='user', columns=['Email', 'PasswdHash', 'Role'], values=f"'{email}', '{passwd}', 1")  # 创建为管理员用户
    else:
        db.insert(table='user', columns=['Email', 'PasswdHash'], values=f"'{email}', '{passwd}'")


def delete_user(user_id: int):
    """ 删除用户 """
    cur = db.delete(table="message", where=f"Auth={user_id}")
    if cur is None:
        return False
    cur = db.delete(table="comment", where=f"Auth={user_id}")
    if cur is None:
        return False
    cur = db.delete(table="blog", where=f"Auth={user_id}")
    if cur is None:
        return False
    cur = db.delete(table="user", where=f"ID={user_id}")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_user_email(user_id):
    """ 获取用户邮箱 """
    cur = db.search(columns=["Email"], table="user", where=f"ID='{user_id}'")
    if cur is None or cur.rowcount == 0:
        return None
    return cur.fetchone()[0]


def get_role_name(role: int):
    """ 获取用户角色名称 """
    cur = db.search(columns=["RoleName"], table="role", where=f"RoleID={role}")
    if cur is None or cur.rowcount == 0:
        return None
    return cur.fetchone()[0]


def check_role(role: int, operate: str):
    """ 检查角色权限（通过角色ID） """
    cur = db.search(columns=[operate], table="role", where=f"RoleID={role}")
    if cur is None or cur.rowcount == 0:
        return False
    return cur.fetchone()[0] == DBBit.BIT_1


def check_role_by_name(role: str, operate: str):
    """ 检查角色权限（通过角色名） """
    cur = db.search(columns=[operate], table="role", where=f"RoleName='{role}")
    if cur is None or cur.rowcount == 0:
        return False
    return cur.fetchone()[0] == DBBit.BIT_1
