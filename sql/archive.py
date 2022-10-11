from sql import db
from sql.cache import (read_archive_from_cache, write_archive_to_cache, delete_archive_from_cache,
                       get_blog_archive_from_cache, write_blog_archive_to_cache, delete_blog_archive_from_cache,
                       delete_all_blog_archive_from_cache)
from typing import Optional


def create_archive(name: str, describe: str):
    """ 创建新归档 """
    name = name.replace("'", "''")
    describe = describe.replace("'", "''")
    cur = db.insert("INSERT INTO archive(Name, DescribeText) "
                    "VALUES (%s, %s)", name, describe)
    if cur is None or cur.rowcount == 0:
        return None
    return cur.lastrowid


def read_archive(archive_id: int):
    """ 获取归档 ID """
    res = read_archive_from_cache(archive_id)
    if res is not None:
        return res

    cur = db.search("SELECT Name, DescribeText "
                    "FROM archive "
                    "WHERE ID=%s", archive_id)
    if cur is None or cur.rowcount == 0:
        return ["", ""]

    res = cur.fetchone()
    write_archive_to_cache(archive_id, *res)
    return res


def get_blog_archive(blog_id: int):
    """ 获取文章的归档 """
    res = get_blog_archive_from_cache(blog_id)
    if res is not None:
        return res

    cur = db.search("SELECT ArchiveID FROM blog_archive_with_name "
                    "WHERE BlogID=%s "
                    "ORDER BY ArchiveName", blog_id)
    if cur is None or cur.rowcount == 0:
        return []

    res = [i[0] for i in cur.fetchall()]
    write_blog_archive_to_cache(blog_id, res)
    return res


def delete_archive(archive_id: int):
    delete_archive_from_cache(archive_id)
    delete_all_blog_archive_from_cache()
    cur = db.delete("DELETE FROM blog_archive WHERE ArchiveID=%s", archive_id)
    if cur is None:
        return False
    cur = db.delete("DELETE FROM archive WHERE ID=%s", archive_id)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def add_blog_to_archive(blog_id: int, archive_id: int):
    delete_blog_archive_from_cache(blog_id)
    cur = db.search("SELECT BlogID FROM blog_archive WHERE BlogID=%s AND ArchiveID=%s", blog_id, archive_id)
    if cur is None:
        return False
    if cur.rowcount > 0:
        return True
    cur = db.insert("INSERT INTO blog_archive(BlogID, ArchiveID) VALUES (%s, %s)", blog_id, archive_id)
    if cur is None or cur.rowcount != 1:
        return False
    return True


def sub_blog_from_archive(blog_id: int, archive_id: int):
    delete_blog_archive_from_cache(blog_id)
    cur = db.delete("DELETE FROM blog_archive WHERE BlogID=%s AND ArchiveID=%s", blog_id, archive_id)
    if cur is None:
        return False
    return True


def get_archive_list(limit: Optional[int] = None, offset: Optional[int] = None):
    """ 获取归档列表 """
    if limit is not None and offset is not None:
        cur = db.search("SELECT ID "
                        "FROM archive "  # TODO: 去除 archive_with_count
                        "ORDER BY Name "
                        "LIMIT %s "
                        "OFFSET %s ", limit, offset)
    else:
        cur = db.search("SELECT ID "
                        "FROM archive "
                        "ORDER BY Name")

    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]
