from sql import db
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
    cur = db.search("SELECT Name, DescribeText "
                    "FROM archive "
                    "WHERE ID=%s", archive_id)
    if cur is None or cur.rowcount == 0:
        return ["", ""]
    return cur.fetchone()


def get_blog_archive(blog_id: int):
    """ 获取文章的归档 """
    cur = db.search("SELECT ArchiveID FROM blog_archive_with_name "
                    "WHERE BlogID=%s "
                    "ORDER BY ArchiveName", blog_id)
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def delete_archive(archive_id: int):
    cur = db.delete("DELETE FROM blog_archive WHERE ArchiveID=%s", archive_id)
    if cur is None:
        return False
    cur = db.delete("DELETE FROM archive WHERE ID=%s", archive_id)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def add_blog_to_archive(blog_id: int, archive_id: int):
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
    cur = db.delete("DELETE FROM blog_archive WHERE BlogID=%s AND ArchiveID=%s", blog_id, archive_id)
    if cur is None:
        return False
    return True


def get_archive_list(limit: Optional[int] = None, offset: Optional[int] = None):
    """ 获取归档列表 """
    if limit is not None and offset is not None:
        cur = db.search("SELECT ID, Name, DescribeText, Count "
                        "FROM archive_with_count "
                        "ORDER BY Count DESC , Name "
                        "LIMIT %s "
                        "OFFSET %s ", limit, offset)
    else:
        cur = db.search("SELECT ID, Name, DescribeText, Count "
                        "FROM archive_with_count "
                        "ORDER BY Count DESC , Name")

    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()
