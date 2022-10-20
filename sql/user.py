from sql import db, DB
from sql.base import DBBit
from sql.cache import (get_user_from_cache, write_user_to_cache, delete_user_from_cache,
                       get_user_email_from_cache, write_user_email_to_cache, delete_user_email_from_cache,
                       get_role_name_from_cache, write_role_name_to_cache, delete_role_name_from_cache,
                       get_role_operate_from_cache, write_role_operate_to_cache, delete_role_operate_from_cache)
import object.user

from typing import List

role_authority = ["WriteBlog", "WriteComment", "WriteMsg", "CreateUser",
                  "ReadBlog", "ReadComment", "ReadMsg", "ReadSecretMsg", "ReadUserInfo",
                  "DeleteBlog", "DeleteComment", "DeleteMsg", "DeleteUser",
                  "ConfigureSystem", "ReadSystem"]


def read_user(email: str, mysql: DB = db, not_cache=False):
    """ 读取用户 """
    if not not_cache:
        res = get_user_from_cache(email)
        if res is not None:
            return res

    cur = mysql.search("SELECT PasswdHash, Role, ID FROM user WHERE Email=%s", email)
    if cur is None or cur.rowcount != 1:
        return ["", -1, -1]

    res = cur.fetchone()
    write_user_to_cache(email, *res)
    return res


def create_user(email: str, passwd: str, mysql: DB = db):
    """ 创建用户 """
    if len(email) == 0:
        return None

    cur = mysql.search("SELECT COUNT(*) FROM user")
    passwd = object.user.User.get_passwd_hash(passwd)
    if cur is None or cur.rowcount == 0 or cur.fetchone()[0] == 0:
        # 创建为管理员用户
        cur = mysql.insert("INSERT INTO user(Email, PasswdHash, Role) "
                           "VALUES (%s, %s, %s)", email, passwd, 1)
    else:
        cur = mysql.insert("INSERT INTO user(Email, PasswdHash) "
                           "VALUES (%s, %s)", email, passwd)
    if cur is None or cur.rowcount != 1:
        return None
    read_user(email, mysql)  # 刷新缓存
    return cur.lastrowid


def delete_user(user_id: int, mysql: DB = db):
    """ 删除用户 """
    delete_user_from_cache(get_user_email(user_id))
    delete_user_email_from_cache(user_id)

    cur = mysql.delete("DELETE FROM message WHERE Auth=%s", user_id)
    if cur is None:
        return False
    cur = mysql.delete("DELETE FROM comment WHERE Auth=%s", user_id)
    if cur is None:
        return False
    cur = mysql.delete("DELETE FROM blog WHERE Auth=%s", user_id)
    if cur is None:
        return False
    cur = mysql.delete("DELETE FROM user WHERE ID=%s", user_id)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def change_passwd_hash(user_email: str, passwd_hash: str, mysql: DB = db):
    delete_user_from_cache(user_email)
    cur = mysql.update("UPDATE user "
                       "SET PasswdHash=%s "
                       "WHERE Email=%s", passwd_hash, user_email)
    read_user(user_email, mysql)  # 刷新缓存
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_user_email(user_id, mysql: DB = db, not_cache=False):
    """ 获取用户邮箱 """
    if not not_cache:
        res = get_user_email_from_cache(user_id)
        if res is not None:
            return res

    cur = mysql.search("SELECT Email FROM user WHERE ID=%s", user_id)
    if cur is None or cur.rowcount == 0:
        return None

    res = cur.fetchone()[0]
    write_user_email_to_cache(user_id, res)
    return res


def __authority_to_sql(authority):
    """ authority 转换为 Update语句, 不检查合法性 """
    sql = []
    args = []
    for i in authority:
        sql.append(f"{i}=%s")
        args.append(authority[i])
    return ",".join(sql), args


def create_role(name: str, authority: List[str], mysql: DB = db):
    cur = db.insert("INSERT INTO role(RoleName) VALUES (%s)", name)
    if cur is None or cur.rowcount == 0:
        return False

    sql, args = __authority_to_sql({i: (1 if i in authority else 0) for i in role_authority})
    cur = mysql.update(f"UPDATE role "
                       f"SET {sql} "
                       f"WHERE RoleName=%s", *args, name)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def delete_role(role_id: int, mysql: DB = db):
    delete_role_name_from_cache(role_id)
    delete_role_operate_from_cache(role_id)

    cur = mysql.delete("DELETE FROM role WHERE RoleID=%s", role_id)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def set_user_role(role_id: int, user_id: str, mysql: DB = db):
    cur = mysql.update("UPDATE user "
                       "SET Role=%s "
                       "WHERE ID=%s", role_id, user_id)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_role_name(role: int, mysql: DB = db, not_cache=False):
    """ 获取用户角色名称 """
    if not not_cache:
        res = get_role_name_from_cache(role)
        if res is not None:
            return res

    cur = mysql.search("SELECT RoleName FROM role WHERE RoleID=%s", role)
    if cur is None or cur.rowcount == 0:
        return None

    res = cur.fetchone()[0]
    write_role_name_to_cache(role, res)
    return res


def __check_operate(operate):
    return operate in role_authority


def check_role(role: int, operate: str, mysql: DB = db, not_cache=False):
    """ 检查角色权限（通过角色ID） """
    if not __check_operate(operate):  # 检查, 防止SQL注入
        return False

    if not not_cache:
        res = get_role_operate_from_cache(role, operate)
        if res is not None:
            return res

    cur = mysql.search(f"SELECT {operate} FROM role WHERE RoleID=%s", role)
    if cur is None or cur.rowcount == 0:
        return False

    res = cur.fetchone()[0] == DBBit.BIT_1
    write_role_operate_to_cache(role, operate, res)
    return res


def get_role_list(mysql: DB = db):
    """ 获取归档列表 """
    cur = mysql.search("SELECT RoleID, RoleName FROM role")
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_role_list_iter(mysql: DB = db):
    """ 获取归档列表 """
    cur = mysql.search("SELECT RoleID, RoleName FROM role")
    if cur is None or cur.rowcount == 0:
        return []
    return cur


def get_user_list_iter(mysql: DB = db):
    """ 获取归档列表 """
    cur = mysql.search("SELECT ID FROM user")
    if cur is None or cur.rowcount == 0:
        return []
    return cur
