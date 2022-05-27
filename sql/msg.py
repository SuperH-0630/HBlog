from sql import db
from typing import Optional


def read_msg_list(limit: Optional[int] = None, offset: Optional[int] = None, show_secret: bool = False):
    if show_secret:
        where = None
    else:
        where = "Secret=0"

    cur = db.search(columns=["MsgID"], table="message_user",
                    limit=limit,
                    where=where,
                    offset=offset,
                    order_by=[("UpdateTime", "DESC")])
    if cur is None or cur.rowcount == 0:
        return []
    return [i[0] for i in cur.fetchall()]


def create_msg(auth: int, content: str, secret: bool = False):
    content = content.replace("'", "''")
    cur = db.insert(table="message",
                    columns=["Auth", "Content", "Secret"],
                    values=f"{auth}, '{content}', {1 if secret else 0}")
    if cur is None or cur.rowcount != 1:
        return None
    return cur.lastrowid


def read_msg(msg_id: int):
    cur = db.search(columns=["Email", "Content", "UpdateTime", "Secret"], table="message_user",
                    where=f"MsgID={msg_id}")
    if cur is None or cur.rowcount == 0:
        return ["", "", 0, False]
    return cur.fetchone()


def delete_msg(msg_id: int):
    cur = db.delete(table="message", where=f"ID={msg_id}")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_msg_count():
    cur = db.search(columns=["count(ID)"], table="message")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]


def get_user_msg_count(user_id: int):
    cur = db.search(columns=["count(ID)"], table="message",
                    where=f"Auth={user_id}")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]
