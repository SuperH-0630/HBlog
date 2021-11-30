from sql import db
from typing import Optional


def create_archive(name: str, describe: str):
    """ 创建新归档 """
    cur = db.insert(table="archive",
                    columns=["Name", "DescribeText"],
                    values=f"'{name}', '{describe}'")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def read_archive(blog_id: int):
    """ 获取文章的归档 """
    cur = db.search(columns=["ArchiveID", "ArchiveName", "DescribeText"], table="blog_archive_with_name",
                    where=f"BlogID={blog_id}")
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def delete_archive(archive_id: int):
    cur = db.delete(table="blog_archive", where=f"ArchiveID={archive_id}")
    if cur is None:
        return False
    cur = db.delete(table="archive", where=f"ID={archive_id}")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_archive_list(limit: Optional[int] = None, offset: Optional[int] = None):
    """ 获取归档列表 """
    cur = db.search(columns=["ID", "Name", "DescribeText", "Count"], table="archive_with_count",
                    limit=limit,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def get_archive_id_by_name(name: str):
    """ 获取归档 ID """
    cur = db.search(columns=["ID", "DescribeText"], table="archive",
                    where=f"Name='{name}'")
    if cur is None or cur.rowcount == 0:
        return None, None
    return cur.fetchone()
