from sql import db


def read_comment(blog_id: int):
    """ 读取文章的 comment """
    cur = db.search(columns=["CommentID", "Auth", "Email", "Context", "UpdateTime"],
                    table="comment_user",
                    where=f"BlogID={blog_id}")
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def create_comment(blog_id: int, user_id: int, context: str):
    """ 新建 comment """
    cur = db.insert(table="comment",
                    columns=["BlogID", "Auth", "Context"],
                    values=f"{blog_id}, {user_id}, '{context}'")
    if cur is None or cur.rowcount == 0:
        return False
    return True


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
