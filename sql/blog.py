from sql import db, DB
from sql.base import DBBit
from sql.archive import add_blog_to_archive
from sql.cache import (write_blog_to_cache, get_blog_from_cache, delete_blog_from_cache,
                       write_blog_count_to_cache, get_blog_count_from_cache, delete_blog_count_from_cache,
                       write_archive_blog_count_to_cache, get_archive_blog_count_from_cache,
                       delete_all_archive_blog_count_from_cache, delete_archive_blog_count_from_cache,
                       write_user_blog_count_to_cache, get_user_blog_count_from_cache,
                       delete_all_user_blog_count_from_cache, delete_user_blog_count_from_cache,
                       delete_blog_archive_from_cache)
import object.archive

from typing import Optional, List


def create_blog(auth_id: int, title: str, subtitle: str, content: str,
                archive_list: List[object.archive.Archive], mysql: DB = db) -> bool:
    """ 写入新的blog """
    delete_blog_count_from_cache()
    delete_user_blog_count_from_cache(auth_id)
    # archive cache 在下面循环删除

    cur = mysql.insert("INSERT INTO blog(Auth, Title, SubTitle, Content) "
                       "VALUES (%s, %s, %s, %s)", auth_id, title, subtitle, content)
    if cur is None or cur.rowcount == 0:
        return False

    blog_id = cur.lastrowid
    for archive in archive_list:
        if not add_blog_to_archive(blog_id, archive.id):
            return False
        delete_archive_blog_count_from_cache(archive.id)
    read_blog(blog_id, mysql)  # 刷新缓存
    return True


def update_blog(blog_id: int, content: str, mysql: DB = db) -> bool:
    """ 更新博客文章 """
    delete_blog_from_cache(blog_id)

    cur = mysql.update("Update blog "
                       "SET UpdateTime=CURRENT_TIMESTAMP(), Content=%s "
                       "WHERE ID=%s", content, blog_id)
    if cur is None or cur.rowcount != 1:
        return False
    read_blog(blog_id, mysql)  # 刷新缓存
    return True


def read_blog(blog_id: int, mysql: DB = db, not_cache=False) -> list:
    """ 读取blog内容 """
    if not not_cache:
        res = get_blog_from_cache(blog_id)
        if res is not None:
            return res

    cur = mysql.search("SELECT Auth, Title, SubTitle, Content, UpdateTime, CreateTime, Top "
                       "FROM blog "
                       "WHERE ID=%s", blog_id)
    if cur is None or cur.rowcount == 0:
        return [-1, "", "", "", 0, -1, False]
    res = cur.fetchone()
    write_blog_to_cache(blog_id, *res, is_db_bit=True)
    return [*res[:6], res[-1] == DBBit.BIT_1]


def delete_blog(blog_id: int, mysql: DB = db):
    delete_blog_count_from_cache()
    delete_all_archive_blog_count_from_cache()
    delete_all_user_blog_count_from_cache()
    delete_blog_from_cache(blog_id)
    delete_blog_archive_from_cache(blog_id)

    conn = mysql.get_connection()
    cur = mysql.delete("DELETE FROM blog_archive WHERE BlogID=%s", blog_id, connection=conn)
    if cur is None:
        conn.rollback()
        conn.close()
        return False

    cur = mysql.delete("DELETE FROM comment WHERE BlogID=%s", blog_id, connection=conn)
    if cur is None:
        conn.rollback()
        conn.close()
        return False

    cur = mysql.delete("DELETE FROM blog WHERE ID=%s", blog_id, connection=conn)
    if cur is None or cur.rowcount == 0:
        conn.rollback()
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def set_blog_top(blog_id: int, top: bool = True, mysql: DB = db):
    delete_blog_from_cache(blog_id)
    cur = mysql.update("UPDATE blog "
                       "SET Top=%s "
                       "WHERE ID=%s", 1 if top else 0, blog_id)
    if cur is None or cur.rowcount != 1:
        return False
    read_blog(blog_id, mysql)  # 刷新缓存
    return True


def get_blog_list(limit: Optional[int] = None, offset: Optional[int] = None, mysql: DB = db) -> list:
    """ 获得 blog 列表 """
    if limit is not None and offset is not None:
        cur = mysql.search("SELECT ID "
                           "FROM blog "
                           "ORDER BY Top DESC, CreateTime DESC, Title, SubTitle "
                           "LIMIT %s OFFSET %s", limit, offset)
    else:
        cur = mysql.search("SELECT ID "
                           "FROM blog "
                           "ORDER BY Top DESC, CreateTime DESC, Title, SubTitle")
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def get_blog_list_iter(mysql: DB = db):
    """ 获得 blog 列表 """
    cur = mysql.search("SELECT ID "
                       "FROM blog "
                       "ORDER BY Top DESC, CreateTime DESC, Title, SubTitle")
    if cur is None or cur.rowcount == 0:
        return []
    return cur


def get_blog_list_not_top(limit: Optional[int] = None, offset: Optional[int] = None, mysql: DB = db) -> list:
    """ 获得blog列表 忽略置顶 """
    if limit is not None and offset is not None:
        cur = mysql.search("SELECT ID "
                           "FROM blog "
                           "ORDER BY CreateTime DESC, Title, SubTitle "
                           "LIMIT %s OFFSET %s", limit, offset)
    else:
        cur = mysql.search("SELECT ID "
                           "FROM blog "
                           "ORDER BY CreateTime DESC, Title, SubTitle")
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def get_archive_blog_list(archive_id, limit: Optional[int] = None,
                          offset: Optional[int] = None,
                          mysql: DB = db) -> list:
    """ 获得指定归档的 blog 列表 """
    if limit is not None and offset is not None:
        cur = mysql.search("SELECT BlogID "
                           "FROM blog_with_archive "
                           "WHERE ArchiveID=%s "
                           "ORDER BY Top DESC, CreateTime DESC, Title, SubTitle "
                           "LIMIT %s OFFSET %s", archive_id, limit, offset)
    else:
        cur = mysql.search("SELECT BlogID "
                           "FROM blog_with_archive "
                           "WHERE ArchiveID=%s "
                           "ORDER BY Top DESC, CreateTime DESC, Title, SubTitle")
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def get_blog_count(mysql: DB = db, not_cache=False) -> int:
    """ 统计 blog 个数 """
    if not not_cache:
        res = get_blog_count_from_cache()
        if res is not None:
            return res

    cur = mysql.search("SELECT COUNT(*) FROM blog")
    if cur is None or cur.rowcount == 0:
        return 0

    res = cur.fetchone()[0]
    write_blog_count_to_cache(res)
    return res


def get_archive_blog_count(archive_id, mysql: DB = db, not_cache=False) -> int:
    """ 统计指定归档的 blog 个数 """
    if not not_cache:
        res = get_archive_blog_count_from_cache(archive_id)
        if res is not None:
            return res

    cur = mysql.search("SELECT COUNT(*) FROM blog_with_archive WHERE ArchiveID=%s", archive_id)
    if cur is None or cur.rowcount == 0:
        return 0

    res = cur.fetchone()[0]
    write_archive_blog_count_to_cache(archive_id, res)
    return res


def get_user_blog_count(user_id: int, mysql: DB = db, not_cache=False) -> int:
    """ 获得指定用户的 blog 个数 """
    if not not_cache:
        res = get_user_blog_count_from_cache(user_id)
        if res is not None:
            return res

    cur = mysql.search("SELECT COUNT(*) FROM blog WHERE Auth=%s", user_id)
    if cur is None or cur.rowcount == 0:
        return 0

    res = cur.fetchone()[0]
    write_user_blog_count_to_cache(user_id, res)
    return res
