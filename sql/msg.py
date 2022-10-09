from sql import db
from typing import Optional


def read_msg_list(limit: Optional[int] = None, offset: Optional[int] = None, show_secret: bool = False):
    if show_secret:
        if limit is not None and offset is not None:
            cur = db.search("SELECT MsgID "
                            "FROM message_user "
                            "ORDER BY UpdateTime DESC "
                            "LIMIT %s "
                            "OFFSET %s", limit, offset)
        else:
            cur = db.search("SELECT MsgID "
                            "FROM message_user "
                            "ORDER BY UpdateTime DESC")
    else:
        if limit is not None and offset is not None:
            cur = db.search("SELECT MsgID "
                            "FROM message_user "
                            "WHERE Secret=0 "
                            "ORDER BY UpdateTime DESC "
                            "LIMIT %s "
                            "OFFSET %s", limit, offset)
        else:
            cur = db.search("SELECT MsgID "
                            "FROM message_user "
                            "WHERE Secret=0 "
                            "ORDER BY UpdateTime DESC")
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
    cur = db.search("SELECT Email, Content, UpdateTime, Secret "
                    "FROM message_user "
                    "WHERE MsgID=%s", msg_id)
    if cur is None or cur.rowcount == 0:
        return ["", "", 0, False]
    return cur.fetchone()


def delete_msg(msg_id: int):
    cur = db.delete(table="message", where=f"ID={msg_id}")
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_msg_count():
    cur = db.search("SELECT COUNT(*) FROM message")
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]


def get_user_msg_count(user_id: int):
    cur = db.search("SELECT COUNT(*) FROM message WHERE Auth=%s", user_id)
    if cur is None or cur.rowcount == 0:
        return 0
    return cur.fetchone()[0]
