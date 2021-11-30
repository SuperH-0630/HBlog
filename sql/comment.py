from sql import db


def get_comment_list(blog_id: int):
    cur = db.search(columns=["Auth", "Email", "Context", "UpdateTime"],
                    table="comment_user",
                    where=f"BlogID={blog_id}")
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


def write_comment(blog_id: int, user_id: int, context: str):
    cur = db.insert(table="comment",
                    columns=["BlogID", "Auth", "Context"],
                    values=f"{blog_id}, {user_id}, '{context}'")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_user_comment_count(user_id: int):
    cur = db.search(columns=["count(ID)"], table="comment",
                    where=f"Auth={user_id}")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]
