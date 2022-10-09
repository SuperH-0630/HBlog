from sql import db


def read_comment_list(blog_id: int):
    """ 读取文章的 comment """
    cur = db.search("SELECT CommentID "
                    "FROM comment_user "
                    "WHERE BlogID=%s "
                    "ORDER BY UpdateTime DESC", blog_id)
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def create_comment(blog_id: int, user_id: int, content: str):
    """ 新建 comment """
    content = content.replace("'", "''")
    cur = db.insert("INSERT INTO comment(BlogID, Auth, Content) "
                    "VALUES (%s, %s, %s)", blog_id, user_id, content)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def read_comment(comment_id: int):
    """ 读取 comment """
    cur = db.search("SELECT BlogID, Email, Content, UpdateTime FROM comment_user WHERE CommentID=%s", comment_id)
    if cur is None or cur.rowcount == 0:
        return [-1, "", "", 0]
    return cur.fetchone()


def delete_comment(comment_id):
    """ 删除评论 """
    cur = db.delete("DELETE FROM comment WHERE ID=%s", comment_id)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_user_comment_count(user_id: int):
    """ 读取指定用户的 comment 个数 """
    cur = db.search("SELECT COUNT(*) FROM comment WHERE Auth=%s", user_id)
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]
