from sql import db
from typing import Optional


def get_msg_list(limit: Optional[int] = None, offset: Optional[int] = None, show_secret: bool = False):
    if show_secret:
        where = None
    else:
        where = "Secret=0"

    cur = db.search(columns=["MsgID", "Auth", "Email", "Context", "UpdateTime", "Secret"], table="message_user",
                    limit=limit,
                    where=where,
                    offset=offset)
    if cur is None or cur.rowcount == 0:
        return []
    return cur.fetchall()


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


def write_msg(auth: int, context: str, secret: bool = False):
    cur = db.insert(table="message",
                    columns=["Auth", "Context", "Secret"],
                    values=f"{auth}, '{context}', {1 if secret else 0}")
    return cur is not None and cur.rowcount == 1
