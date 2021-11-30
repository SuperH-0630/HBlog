from sql import db
from typing import Optional


def create_file(name: str, describe: str):
    cur = db.insert(table="file",
                    columns=["Name", "DescribeText"],
                    values=f"'{name}', '{describe}'")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_blog_file(blog_id: int):
    cur = db.search(columns=["FileID", "FileName", "DescribeText"], table="blog_file_with_name",
                    where=f"BlogID={blog_id}")
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_file_list(limit: Optional[int] = None, offset: Optional[int] = None):
    cur = db.search(columns=["ID", "Name", "DescribeText", "Count"], table="file_with_count",
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_file_id(name: str):
    cur = db.search(columns=["ID", "DescribeText"], table="file",
                    where=f"Name='{name}'")
    if cur is None or cur.rowcount == 0:
        return None, None
    return cur.fetchone()
