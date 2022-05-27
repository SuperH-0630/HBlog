from sql import db


def read_comment_list(blog_id: int):
    """ 读取文章的 comment """
    cur = db.search(columns=["CommentID"],
                    table="comment_user",
                    where=f"BlogID={blog_id}",
                    order_by=[("UpdateTime", "DESC")])
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def create_comment(blog_id: int, user_id: int, content: str):
    """ 新建 comment """
    content = content.replace("'", "''")
    cur = db.insert(table="comment",
                    columns=["BlogID", "Auth", "Content"],
                    values=f"{blog_id}, {user_id}, '{content}'")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def read_comment(comment_id: int):
    """ 读取 comment """
    cur = db.search(columns=["BlogID", "Email", "Content", "UpdateTime"],
                    table="comment_user",
                    where=f"CommentID={comment_id}")
    if cur is None or cur.rowcount == 0:
        return [-1, "", "", 0]
    return cur.fetchone()


def delete_comment(comment_id):
    """ 删除评论 """
    cur = db.delete(table="comment", where=f"ID={comment_id}")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_user_comment_count(user_id: int):
    """ 读取指定用户的 comment 个数 """
    cur = db.search(columns=["count(ID)"], table="comment",
                    where=f"Auth={user_id}")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]
