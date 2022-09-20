from sql import db
from typing import Optional


def create_archive(name: str, describe: str):
    """ 创建新归档 """
    name = name.replace("'", "''")
    describe = describe.replace("'", "''")
    cur = db.insert(table="archive",
                    columns=["Name", "DescribeText"],
                    values=f"'{name}', '{describe}'")
    if cur is None or cur.rowcount == 0:
        return None
    return cur.lastrowid


def read_archive(archive_id: int):
    """ 获取归档 ID """
    cur = db.search(columns=["Name", "DescribeText"],
                    table="archive",
                    where=f"ID={archive_id}")
    if cur is None or cur.rowcount == 0:
        return ["", ""]
    return cur.fetchone()


def get_blog_archive(blog_id: int):
    """ 获取文章的归档 """
    cur = db.search(columns=["ArchiveID"],
                    table="blog_archive_with_name",
                    where=f"BlogID={blog_id}",
                    order_by=[("ArchiveName", "ASC")])
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def delete_archive(archive_id: int):
    cur = db.delete(table="blog_archive", where=f"ArchiveID={archive_id}")
    if cur is None:
        return False
    cur = db.delete(table="archive", where=f"ID={archive_id}")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def add_blog_to_archive(blog_id: int, archive_id: int):
    cur = db.search(columns=["BlogID"], table="blog_archive", where=f"BlogID={blog_id} AND ArchiveID={archive_id}")
    if cur is None:
        return False
    if cur.rowcount > 0:
        return True
    cur = db.insert(table="blog_archive", columns=["BlogID", "ArchiveID"], values=f"{blog_id}, {archive_id}")
    if cur is None or cur.rowcount != 1:
        return False
    return True


def sub_blog_from_archive(blog_id: int, archive_id: int):
    cur = db.delete(table="blog_archive", where=f"BlogID={blog_id} AND ArchiveID={archive_id}")
    if cur is None:
        return False
    return True


def get_archive_list(limit: Optional[int] = None, offset: Optional[int] = None):
    """ 获取归档列表 """
    cur = db.search(columns=["ID", "Name", "DescribeText", "Count"], table="archive_with_count",
                    limit=limit,
                    offset=offset,
                    order_by=[("Count", "DESC"), ("Name", "ASC")])
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()
