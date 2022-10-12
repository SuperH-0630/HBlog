from sql import db
from sql.cache import (get_msg_from_cache, write_msg_to_cache, delete_msg_from_cache,
                       get_msg_cout_from_cache, write_msg_count_to_cache, delete_msg_count_from_cache,
                       get_user_msg_count_from_cache, write_user_msg_count_to_cache,
                       delete_all_user_msg_count_from_cache, delete_user_msg_count_from_cache)

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
    delete_msg_count_from_cache()
    delete_user_msg_count_from_cache(auth)

    content = content.replace("'", "''")
    cur = db.insert("INSERT INTO message(Auth, Content, Secret) "
                    "VALUES (%s, %s, %s)", auth, content, 1 if secret else 0)
    if cur is None or cur.rowcount != 1:
        return None
    return cur.lastrowid


def read_msg(msg_id: int):
    res = get_msg_from_cache(msg_id)
    if res is not None:
        return res

    cur = db.search("SELECT Email, Content, UpdateTime, Secret "
                    "FROM message_user "
                    "WHERE MsgID=%s", msg_id)
    if cur is None or cur.rowcount == 0:
        return ["", "", "0", False]

    res = cur.fetchone()
    write_msg_to_cache(msg_id, *res)
    return res


def delete_msg(msg_id: int):
    delete_msg_from_cache(msg_id)
    delete_msg_count_from_cache()
    delete_all_user_msg_count_from_cache()
    cur = db.delete("DELETE FROM message WHERE ID=%s", msg_id)
    if cur is None or cur.rowcount == 0:
        return False
    return True


def get_msg_count():
    res = get_msg_cout_from_cache()
    if res is not None:
        return res

    cur = db.search("SELECT COUNT(*) FROM message")
    if cur is None or cur.rowcount == 0:
        return 0
    res = cur.fetchone()[0]
    write_msg_count_to_cache(res)
    return res


def get_user_msg_count(user_id: int):
    res = get_user_msg_count_from_cache(user_id)
    if res is not None:
        return res

    cur = db.search("SELECT COUNT(*) FROM message WHERE Auth=%s", user_id)
    if cur is None or cur.rowcount == 0:
        return 0
    res = cur.fetchone()[0]
    write_user_msg_count_to_cache(user_id, res)
    return res
