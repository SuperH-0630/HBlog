from sql import db
from sql.base import DBBit
import object.user

from typing import List


role_authority = ["WriteBlog", "WriteComment", "WriteMsg", "CreateUser",
                  "ReadBlog", "ReadComment", "ReadMsg", "ReadSecretMsg", "ReadUserInfo",
                  "DeleteBlog", "DeleteComment", "DeleteMsg", "DeleteUser",
                  "ConfigureSystem", "ReadSystem"]


def read_user(email: str):
    """ 读取用户 """
    cur = db.search(columns=["PasswdHash", "Role", "ID"], table="user", where=f"Email='{email}'")
    if cur is None or cur.rowcount != 1:
        return ["", -1, -1]
    return cur.fetchone()


def create_user(email: str, passwd: str):
    """ 创建用户 """
    email = email.replace("'", "''")
    if len(email) == 0:
        return None

    cur = db.search(columns=["count(Email)"], table="user")  # 统计个数
    passwd = object.user.User.get_passwd_hash(passwd)
    if cur is None or cur.rowcount == 0 or cur.fetchone()[0] == 0:
        # 创建为管理员用户
        cur = db.insert(table='user', columns=['Email', 'PasswdHash', 'Role'], values=f"'{email}', '{passwd}', 1")
    else:
        cur = db.insert(table='user', columns=['Email', 'PasswdHash'], values=f"'{email}', '{passwd}'")
    if cur is None or cur.rowcount != 1:
        return None
    return cur.lastrowid


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


def create_role(name: str, authority: List[str]):
    name = name.replace("'", "''")
    cur = db.insert(table="role", columns=["RoleName"], values=f"'{name}'", not_commit=True)
    if cur is None or cur.rowcount == 0:
        return False

    kw = {}
    for i in role_authority:
        kw[i] = '0'
    for i in authority:
        if i in role_authority:
            kw[i] = '1'

    cur = db.update(table='role', kw=kw, where=f"RoleName='{name}'")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def delete_role(role_id: int):
    cur = db.delete(table="role", where=f"RoleID={role_id}")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def set_user_role(role_id: int, user_id: str):
    cur = db.update(table="user", kw={"Role": f"{role_id}"}, where=f"ID={user_id}")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def change_passwd_hash(user_id: int, passwd_hash: str):
    cur = db.update(table='user', kw={'PasswdHash': f"'{passwd_hash}'"}, where=f'ID={user_id}')
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
    role = role.replace("'", "''")
    cur = db.search(columns=[operate], table="role", where=f"RoleName='{role}'")
    if cur is None or cur.rowcount == 0:
        return False
    return cur.fetchone()[0] == DBBit.BIT_1


def get_role_id_by_name(role: str):
    """ 检查角色权限（通过角色名） """
    role = role.replace("'", "''")
    cur = db.search(columns=["RoleID"], table="role", where=f"RoleName='{role}'")
    if cur is None or cur.rowcount == 0:
        return None
    return cur.fetchone()[0]


def get_role_list():
    """ 获取归档列表 """
    cur = db.search(columns=["RoleID", "RoleName"], table="role")
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()
