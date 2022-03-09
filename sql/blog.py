from sql import db
from typing import Optional, List
import object.archive


def create_blog(auth_id: int, title: str, subtitle: str, context: str,
                archive_list: List[object.archive.Archive]) -> bool:
    """ 写入新的blog """
    title = title.replace("'", "''")
    subtitle = subtitle.replace("'", "''")
    context = context.replace("'", "''")
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


def update_blog(blog_id: int, context: str) -> bool:
    """ 更新博客文章 """
    context = context.replace("'", "''")
    cur = db.update(table="blog",
                    kw={"UpdateTime": "CURRENT_TIMESTAMP()", "Context": f"'{context}'"},
                    where=f"ID={blog_id}")
    if cur is None or cur.rowcount != 1:
        return False
    return True


def read_blog(blog_id: int) -> list:
    """ 读取blog内容 """
    cur = db.search(columns=["Auth", "Title", "SubTitle", "Context", "UpdateTime", "Top"],
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
    """ 获得 blog 列表 """
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
