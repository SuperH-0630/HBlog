from sql import db
from typing import Optional


def create_file(name: str, describe: str):
    """ 创建新归档 """
    cur = db.insert(table="file",
                    columns=["Name", "DescribeText"],
                    values=f"'{name}', '{describe}'")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def read_file(blog_id: int):
    """ 获取文章的归档 """
    cur = db.search(columns=["FileID", "FileName", "DescribeText"], table="blog_file_with_name",
                    where=f"BlogID={blog_id}")
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def delete_file(file_id: int):
    cur = db.delete(table="blog_file", where=f"FileID={file_id}")
    if cur is None:
        return False
    cur = db.delete(table="file", where=f"ID={file_id}")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_file_list(limit: Optional[int] = None, offset: Optional[int] = None):
    """ 获取归档列表 """
    cur = db.search(columns=["ID", "Name", "DescribeText", "Count"], table="file_with_count",
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_file_id_by_name(name: str):
    """ 获取归档 ID """
    cur = db.search(columns=["ID", "DescribeText"], table="file",
                    where=f"Name='{name}'")
    if cur is None or cur.rowcount == 0:
        return None, None
    return cur.fetchone()
