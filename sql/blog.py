from sql import db
from typing import Optional, List
import core.file


def write_blog(auth_id: int, title: str, subtitle:str, context: str, file_list: List[core.file.File]) -> bool:
    cur = db.insert(table="blog", columns=["Auth", "Title", "SubTitle", "Context"],
                    values=f"{auth_id}, '{title}', '{subtitle}', '{context}'")
    if cur is None or cur.rowcount == 0:
        return False
    blog_id = cur.lastrowid
    for file in file_list:
        cur = db.insert(table="blog_file", columns=["BlogID", "FileID"],
                        values=f"{blog_id}, {file.id}")
        if cur is None or cur.rowcount == 0:
            return False
    return True


def read_blog(blog_id: int) -> list:
    cur = db.search(columns=["Auth", "Title", "SubTitle", "Context", "Quote", "Spider", "UpdateTime", "Top"],
                    table="blog",
                    where=f"ID={blog_id}")
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchone()


def get_blog_list(limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    cur = db.search(columns=["ID", "Title", "SubTitle", "UpdateTime", "Top"], table="blog_with_top",
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_blog_list_not_top(limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    cur = db.search(columns=["ID", "Title", "SubTitle", "UpdateTime"], table="blog",
                    order_by=[("UpdateTime", "DESC")],
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_blog_count() -> int:
    cur = db.search(columns=["count(ID)"], table="blog")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]


def get_blog_list_with_file(file_id, limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    cur = db.search(columns=["BlogID", "Title", "SubTitle", "UpdateTime", "Top"], table="blog_with_file",
                    where=f"FileID={file_id}",
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_blog_with_file_count(file_id) -> int:
    cur = db.search(columns=["count(ID)"], table="blog_with_file",
                    where=f"FileID={file_id}")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]


def get_blog_user_count(user_id: int) -> int:
    cur = db.search(columns=["count(ID)"], table="blog",
                    where=f"Auth={user_id}")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]
