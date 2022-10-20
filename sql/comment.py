from sql import db, DB
from sql.cache import (get_comment_from_cache, write_comment_to_cache, delete_comment_from_cache,
                       get_user_comment_count_from_cache, write_user_comment_count_to_cache,
                       delete_all_user_comment_count_from_cache, delete_user_comment_count_from_cache)


def read_comment_list(blog_id: int, mysql: DB = db):
    """ 读取文章的 comment """
    cur = mysql.search("SELECT CommentID "
                       "FROM comment_user "
                       "WHERE BlogID=%s "
                       "ORDER BY UpdateTime DESC", blog_id)
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def read_comment_list_iter(mysql: DB = db):
    """ 读取文章的 comment """
    cur = mysql.search("SELECT CommentID "
                       "FROM comment_user "
                       "ORDER BY UpdateTime DESC")
    if cur is None or cur.rowcount == 0:
        return []
    return cur


def create_comment(blog_id: int, user_id: int, content: str, mysql: DB = db):
    """ 新建 comment """
    delete_user_comment_count_from_cache(user_id)

    cur = mysql.insert("INSERT INTO comment(BlogID, Auth, Content) "
                       "VALUES (%s, %s, %s)", blog_id, user_id, content)
    if cur is None or cur.rowcount == 0:
        return False
    read_comment(cur.lastrowid, mysql)  # 刷新缓存
    return True


def read_comment(comment_id: int, mysql: DB = db, not_cache=False):
    """ 读取 comment """
    if not not_cache:
        res = get_comment_from_cache(comment_id)
        if res is not None:
            return res

    cur = mysql.search("SELECT BlogID, Email, Content, UpdateTime FROM comment_user WHERE CommentID=%s", comment_id)
    if cur is None or cur.rowcount == 0:
        return [-1, "", "", 0]

    res = cur.fetchone()
    write_comment_to_cache(comment_id, *res)
    return res


def delete_comment(comment_id: int, mysql: DB = db):
    """ 删除评论 """
    delete_comment_from_cache(comment_id)
    delete_all_user_comment_count_from_cache()
    cur = mysql.delete("DELETE FROM comment WHERE ID=%s", comment_id)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_user_comment_count(user_id: int, mysql: DB = db, not_cache=False):
    """ 读取指定用户的 comment 个数 """
    if not not_cache:
        res = get_user_comment_count_from_cache(user_id)
        if res is not None:
            return res

    cur = mysql.search("SELECT COUNT(*) FROM comment WHERE Auth=%s", user_id)
    if cur is None or cur.rowcount == 0:
        return 0

    res = cur.fetchone()[0]
    write_user_comment_count_to_cache(user_id, res)
    return res
