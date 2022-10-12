from sql import db
from sql.archive import add_blog_to_archive
from sql.cache import (write_blog_to_cache, get_blog_from_cache, delete_blog_from_cache,
                       write_blog_count_to_cache, get_blog_count_from_cache, delete_blog_count_from_cache,
                       write_archive_blog_count_to_cache, get_archive_blog_count_from_cache,
                       delete_all_archive_blog_count_from_cache, delete_archive_blog_count_from_cache,
                       write_user_blog_count_to_cache, get_user_blog_count_from_cache,
                       delete_all_user_blog_count_from_cache, delete_user_blog_count_from_cache,
                       delete_blog_archive_from_cache)
import object.archive


from typing import Optional, List


def create_blog(auth_id: int, title: str, subtitle: str, content: str,
                archive_list: List[object.archive.Archive]) -> bool:
    """ 写入新的blog """
    delete_blog_count_from_cache()
    delete_user_blog_count_from_cache(auth_id)
    # archive cache 在下面循环删除

    title = title.replace("'", "''")
    subtitle = subtitle.replace("'", "''")
    content = content.replace("'", "''")
    cur = db.insert("INSERT INTO blog(Auth, Title, SubTitle, Content) "
                    "VALUES (%s, %s, %s, %s)", auth_id, title, subtitle, content)
    if cur is None or cur.rowcount == 0:
        return False

    blog_id = cur.lastrowid
    for archive in archive_list:
        delete_archive_blog_count_from_cache(archive.id)
        if not add_blog_to_archive(blog_id, archive.id):
            return False

    return True


def update_blog(blog_id: int, content: str) -> bool:
    """ 更新博客文章 """
    delete_blog_from_cache(blog_id)

    content = content.replace("'", "''")
    cur = db.update("Update blog "
                    "SET UpdateTime=CURRENT_TIMESTAMP(), Content=%s "
                    "WHERE ID=%s", content, blog_id)
    if cur is None or cur.rowcount != 1:
        return False
    return True


def read_blog(blog_id: int) -> list:
    """ 读取blog内容 """
    res = get_blog_from_cache(blog_id)
    if res is not None:
        return res

    cur = db.search("SELECT Auth, Title, SubTitle, Content, UpdateTime, CreateTime, Top "
                    "FROM blog "
                    "WHERE ID=%s", blog_id)
    if cur is None or cur.rowcount == 0:
        return [-1, "", "", "", 0, -1, False]
    res = cur.fetchone()
    write_blog_to_cache(blog_id, *res)
    return res


def delete_blog(blog_id: int):
    delete_blog_count_from_cache()
    delete_all_archive_blog_count_from_cache()
    delete_all_user_blog_count_from_cache()
    delete_blog_from_cache(blog_id)
    delete_blog_archive_from_cache(blog_id)

    cur = db.delete("DELETE FROM blog_archive WHERE BlogID=%s", blog_id)
    if cur is None:
        return False
    cur = db.delete("DELETE FROM comment WHERE BlogID=%s", blog_id)
    if cur is None:
        return False
    cur = db.delete("DELETE FROM blog WHERE ID=%s", blog_id)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def set_blog_top(blog_id: int, top: bool = True):
    delete_blog_from_cache(blog_id)
    cur = db.update("UPDATE blog "
                    "SET Top=%s "
                    "WHERE ID=%s", 1 if top else 0, blog_id)
    if cur is None or cur.rowcount != 1:
        return False
    return True


def get_blog_list(limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    """ 获得 blog 列表 """
    if limit is not None and offset is not None:
        cur = db.search("SELECT ID "
                        "FROM blog "
                        "ORDER BY Top DESC, CreateTime DESC, Title, SubTitle "
                        "LIMIT %s OFFSET %s", limit, offset)
    else:
        cur = db.search("SELECT ID "
                        "FROM blog "
                        "ORDER BY Top DESC, CreateTime DESC, Title, SubTitle")
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def get_blog_list_not_top(limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    """ 获得blog列表 忽略置顶 """
    if limit is not None and offset is not None:
        cur = db.search("SELECT ID "
                        "FROM blog "
                        "ORDER BY CreateTime DESC, Title, SubTitle "
                        "LIMIT %s OFFSET %s", limit, offset)
    else:
        cur = db.search("SELECT ID "
                        "FROM blog "
                        "ORDER BY CreateTime DESC, Title, SubTitle")
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def get_archive_blog_list(archive_id, limit: Optional[int] = None, offset: Optional[int] = None) -> list:
    """ 获得指定归档的 blog 列表 """
    if limit is not None and offset is not None:
        cur = db.search("SELECT BlogID "
                        "FROM blog_with_archive "
                        "WHERE ArchiveID=%s "
                        "ORDER BY Top DESC, CreateTime DESC, Title, SubTitle "
                        "LIMIT %s OFFSET %s", archive_id, limit, offset)
    else:
        cur = db.search("SELECT BlogID "
                        "FROM blog_with_archive "
                        "WHERE ArchiveID=%s "
                        "ORDER BY Top DESC, CreateTime DESC, Title, SubTitle")
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def get_blog_count() -> int:
    """ 统计 blog 个数 """
    res = get_blog_count_from_cache()
    if res is not None:
        return res

    cur = db.search("SELECT COUNT(*) FROM blog")
    if cur is None or cur.rowcount == 0:
        return 0

    res = cur.fetchone()[0]
    write_blog_count_to_cache(res)
    return res


def get_archive_blog_count(archive_id) -> int:
    """ 统计指定归档的 blog 个数 """
    res = get_archive_blog_count_from_cache(archive_id)
    if res is not None:
        return res

    cur = db.search("SELECT COUNT(*) FROM blog_with_archive WHERE ArchiveID=%s", archive_id)
    if cur is None or cur.rowcount == 0:
        return 0

    res = cur.fetchone()[0]
    write_archive_blog_count_to_cache(archive_id, res)
    return res


def get_user_blog_count(user_id: int) -> int:
    """ 获得指定用户的 blog 个数 """
    res = get_user_blog_count_from_cache(user_id)
    if res is not None:
        return res

    cur = db.search("SELECT COUNT(*) FROM blog WHERE Auth=%s", user_id)
    if cur is None or cur.rowcount == 0:
        return 0

    res = cur.fetchone()[0]
    write_user_blog_count_to_cache(user_id, res)
    return res
