from sql import db
from typing import Optional, List
import core.archive


def create_blog(auth_id: int, title: str, subtitle:str, context: str, archive_list: List[core.archive.Archive]) -> bool:
    """写入新的blog"""
    cur = db.insert(table="blog", columns=["Auth", "Title", "SubTitle", "Context"],
                    values=f"{auth_id}, '{title}', '{subtitle}', '{context}'")
    if cur is None or cur.rowcount == 0:
        return False
    blog_id = cur.lastrowid
    for archive in archive_list:
        cur = db.insert(table="blog_archive", columns=["BlogID", "ArchiveID"],
                        values=f"{blog_id}, {archive.archive_id}")
        if cur is None or cur.rowcount == 0:
            return False
    return True


def read_blog(blog_id: int) -> list:
    """读取blog内容"""
    cur = db.search(columns=["Auth", "Title", "SubTitle", "Context", "Quote", "Spider", "UpdateTime", "Top"],
                    table="blog",
                    where=f"ID={blog_id}")
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchone()


def delete_blog(blog_id: int):
    cur = db.delete(table="blog_archive", where=f"BlogID={blog_id}")
    if cur is None:
        return False
    cur = db.delete(table="comment", where=f"BlogID={blog_id}")
    if cur is None:
        return False
    cur = db.delete(table="blog", where=f"ID={blog_id}")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_blog_list(limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    """获得 blog 列表"""
    cur = db.search(columns=["ID", "Title", "SubTitle", "UpdateTime", "Top"], table="blog_with_top",
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_blog_list_not_top(limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    """ 获得blog列表 忽略置顶 """
    cur = db.search(columns=["ID", "Title", "SubTitle", "UpdateTime"], table="blog",
                    order_by=[("UpdateTime", "DESC")],
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_blog_count() -> int:
    """ 统计 blog 个数 """
    cur = db.search(columns=["count(ID)"], table="blog")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]


def get_archive_blog_list(archive_id, limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    """ 获得指定归档的 blog 列表 """
    cur = db.search(columns=["BlogID", "Title", "SubTitle", "UpdateTime", "Top"], table="blog_with_archive",
                    where=f"ArchiveID={archive_id}",
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_archive_blog_count(archive_id) -> int:
    """ 统计指定归档的 blog 个数 """
    cur = db.search(columns=["count(ID)"], table="blog_with_archive",
                    where=f"ArchiveID={archive_id}")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]


def get_user_user_count(user_id: int) -> int:
    """ 获得指定用户的 blog 个数 """
    cur = db.search(columns=["count(ID)"], table="blog",
                    where=f"Auth={user_id}")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]
