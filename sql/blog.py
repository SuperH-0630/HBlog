from sql import db
from sql.archive import add_blog_to_archive
from typing import Optional, List
import object.archive


def create_blog(auth_id: int, title: str, subtitle: str, content: str,
                archive_list: List[object.archive.Archive]) -> bool:
    """ 写入新的blog """
    title = title.replace("'", "''")
    subtitle = subtitle.replace("'", "''")
    content = content.replace("'", "''")
    cur = db.insert(table="blog", columns=["Auth", "Title", "SubTitle", "Content"],
                    values=f"{auth_id}, '{title}', '{subtitle}', '{content}'")
    if cur is None or cur.rowcount == 0:
        return False
    blog_id = cur.lastrowid
    for archive in archive_list:
        if not add_blog_to_archive(blog_id, archive.id):
            return False
    return True


def update_blog(blog_id: int, content: str) -> bool:
    """ 更新博客文章 """
    content = content.replace("'", "''")
    cur = db.update(table="blog",
                    kw={"UpdateTime": "CURRENT_TIMESTAMP()", "Content": f"'{content}'"},
                    where=f"ID={blog_id}")
    if cur is None or cur.rowcount != 1:
        return False
    return True


def read_blog(blog_id: int) -> list:
    """ 读取blog内容 """
    cur = db.search(columns=["Auth", "Title", "SubTitle", "Content", "UpdateTime", "CreateTime", "Top"],
                    table="blog",
                    where=f"ID={blog_id}")
    if cur is None or cur.rowcount == 0:
        return [-1, "", "", "", 0, -1, False]
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


def set_blog_top(blog_id: int, top: bool = True):
    cur = db.update(table="blog", kw={"Top": "1" if top else "0"}, where=f"ID={blog_id}")
    if cur is None or cur.rowcount != 1:
        return False
    return True


def get_blog_list(limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    """ 获得 blog 列表 """
    cur = db.search(columns=["ID", "Title", "SubTitle", "UpdateTime", "CreateTime", "Top"], table="blog_with_top",
                    order_by=[("Top", "DESC"), ("CreateTime", "DESC"), ("Title", "ASC"), ("SubTitle", "ASC")],
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_blog_list_not_top(limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    """ 获得blog列表 忽略置顶 """
    cur = db.search(columns=["ID", "Title", "SubTitle", "UpdateTime", "CreateTime"], table="blog",
                    order_by=[("CreateTime", "DESC"), ("Title", "ASC"), ("SubTitle", "ASC")],
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
    cur = db.search(columns=["BlogID", "Title", "SubTitle", "UpdateTime", "CreateTime", "Top"],
                    table="blog_with_archive",
                    order_by=[("Top", "DESC"), ("CreateTime", "DESC"), ("Title", "ASC"), ("SubTitle", "ASC")],
                    where=f"ArchiveID={archive_id}",
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_archive_blog_count(archive_id) -> int:
    """ 统计指定归档的 blog 个数 """
    cur = db.search(columns=["count(BlogID)"], table="blog_with_archive",
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
