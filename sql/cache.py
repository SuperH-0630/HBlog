from sql import cache, DB
from sql.base import DBBit
from configure import conf

from redis import RedisError
from functools import wraps
from datetime import datetime

CACHE_TIME = int(conf["CACHE_EXPIRE"])
CACHE_PREFIX = conf["CACHE_PREFIX"]


def __try_redis(ret=None):
    def try_redis(func):
        @wraps(func)
        def try_func(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except RedisError:
                cache.logger.error(f"Redis error with {args} {kwargs}", exc_info=True, stack_info=True)
                return ret
            return res

        return try_func

    return try_redis


@__try_redis(None)
def get_msg_from_cache(msg_id: int):
    msg = cache.hgetall(f"{CACHE_PREFIX}:msg:{msg_id}")
    if len(msg) != 4:
        return None
    return [msg.get("Email", ""),
            msg.get("Content"),
            datetime.fromtimestamp(float(msg.get("UpdateTime", 0.0))),
            msg.get("Secret", "False") == "True"]


@__try_redis(None)
def write_msg_to_cache(msg_id: int, email: str, content: str, update_time: str | datetime, secret: bool,
                       is_db_bit=False):
    cache_name = f"{CACHE_PREFIX}:msg:{msg_id}"
    cache.delete(cache_name)
    cache.hset(cache_name, mapping={
        "Email": email,
        "Content": content,
        "UpdateTime": datetime.timestamp(update_time),
        "Secret": str(secret == DBBit.BIT_1 if is_db_bit else secret)
    })
    cache.expire(cache_name, CACHE_TIME)


@__try_redis(None)
def delete_msg_from_cache(msg_id: int):
    cache.delete(f"{CACHE_PREFIX}:msg:{msg_id}")


@__try_redis(None)
def get_msg_cout_from_cache():
    count = cache.get(f"{CACHE_PREFIX}:msg_count")
    if count is not None:
        return int(count)


@__try_redis(None)
def write_msg_count_to_cache(count):
    count = cache.set(f"{CACHE_PREFIX}:msg_count", str(count))
    cache.expire(f"{CACHE_PREFIX}:msg_count", CACHE_TIME)
    return count


@__try_redis(None)
def delete_msg_count_from_cache():
    cache.delete(f"{CACHE_PREFIX}:msg_count")


@__try_redis(None)
def get_user_msg_count_from_cache(user_id: int):
    count = cache.get(f"{CACHE_PREFIX}:msg_count:{user_id}")
    if count is not None:
        return int(count)


@__try_redis(None)
def write_user_msg_count_to_cache(user_id, count):
    cache_name = f"{CACHE_PREFIX}:msg_count:{user_id}"
    count = cache.set(cache_name, str(count))
    cache.expire(cache_name, CACHE_TIME)
    return count


@__try_redis(None)
def delete_user_msg_count_from_cache(user_id):
    cache.delete(f"{CACHE_PREFIX}:msg_count:{user_id}")


@__try_redis(None)
def delete_all_user_msg_count_from_cache():
    for i in cache.keys(f"{CACHE_PREFIX}:msg_count:*"):
        cache.delete(i)


@__try_redis(None)
def get_blog_from_cache(blog_id: int):
    blog = cache.hgetall(f"{CACHE_PREFIX}:blog:{blog_id}")
    if len(blog) != 7:
        return None
    return [int(blog.get("Auth", -1)),
            blog.get("Title"),
            blog.get("SubTitle"),
            blog.get("Content"),
            datetime.fromtimestamp(float(blog.get("UpdateTime", 0.0))),
            datetime.fromtimestamp(float(blog.get("CreateTime", 0.0))),
            blog.get("Top", "False") == "True"]


@__try_redis(None)
def write_blog_to_cache(blog_id: int, auth_id: str, title: str, subtitle: str, content: str,
                        update_time: str | datetime, create_time: str | datetime, top: bool, is_db_bit=False):
    cache_name = f"{CACHE_PREFIX}:blog:{blog_id}"
    cache.delete(cache_name)
    cache.hset(cache_name, mapping={
        "Auth": auth_id,
        "Title": title,
        "SubTitle": subtitle,
        "Content": content,
        "UpdateTime": datetime.timestamp(update_time),
        "CreateTime": datetime.timestamp(create_time),
        "Top": str(top == DBBit.BIT_1 if is_db_bit else top)
    })
    cache.expire(cache_name, CACHE_TIME)


@__try_redis(None)
def delete_blog_from_cache(blog_id: int):
    cache.delete(f"{CACHE_PREFIX}:blog:{blog_id}")


@__try_redis(None)
def get_blog_count_from_cache():
    count = cache.get(f"{CACHE_PREFIX}:blog_count")
    if count is not None:
        return int(count)


@__try_redis(None)
def write_blog_count_to_cache(count):
    count = cache.set(f"{CACHE_PREFIX}:blog_count", str(count))
    cache.expire(f"{CACHE_PREFIX}:blog_count", CACHE_TIME)
    return count


@__try_redis(None)
def delete_blog_count_from_cache():
    cache.delete(f"{CACHE_PREFIX}:blog_count")


@__try_redis(None)
def get_archive_blog_count_from_cache(archive_id: int):
    count = cache.get(f"{CACHE_PREFIX}:blog_count:archive:{archive_id}")
    if count is not None:
        return int(count)


@__try_redis(None)
def write_archive_blog_count_to_cache(archive_id, count):
    cache_name = f"{CACHE_PREFIX}:blog_count:archive:{archive_id}"
    count = cache.set(cache_name, str(count))
    cache.expire(cache_name, CACHE_TIME)
    return count


@__try_redis(None)
def delete_all_archive_blog_count_from_cache():
    for i in cache.keys(f"{CACHE_PREFIX}:blog_count:archive:*"):
        cache.delete(i)


@__try_redis(None)
def delete_archive_blog_count_from_cache(archive_id: int):
    cache.delete(f"{CACHE_PREFIX}:blog_count:archive:{archive_id}")


@__try_redis(None)
def get_user_blog_count_from_cache(user_id: int):
    count = cache.get(f"{CACHE_PREFIX}:blog_count:user:{user_id}")
    if count is not None:
        return int(count)


@__try_redis(None)
def write_user_blog_count_to_cache(user_id, count):
    cache_name = f"{CACHE_PREFIX}:blog_count:user:{user_id}"
    count = cache.set(cache_name, str(count))
    cache.expire(cache_name, CACHE_TIME)
    return count


@__try_redis(None)
def delete_all_user_blog_count_from_cache():
    for i in cache.keys(f"{CACHE_PREFIX}:blog_count:user:*"):
        cache.delete(i)


@__try_redis(None)
def delete_user_blog_count_from_cache(user_id: int):
    cache.delete(f"{CACHE_PREFIX}:blog_count:user:{user_id}")


@__try_redis(None)
def get_archive_from_cache(archive_id: int):
    archive = cache.hgetall(f"{CACHE_PREFIX}:archive:{archive_id}")
    if len(archive) != 2:
        return None
    return [archive.get("Name", ""), archive.get("DescribeText")]


@__try_redis(None)
def write_archive_to_cache(archive_id: int, name: str, describe: str):
    cache_name = f"{CACHE_PREFIX}:archive:{archive_id}"
    cache.delete(cache_name)
    cache.hset(cache_name, mapping={
        "Name": name,
        "DescribeText": describe,
    })
    cache.expire(cache_name, CACHE_TIME)


@__try_redis(None)
def delete_archive_from_cache(archive_id: int):
    cache.delete(f"{CACHE_PREFIX}:archive:{archive_id}")


@__try_redis(None)
def get_blog_archive_from_cache(blog_id: int):
    blog_archive = cache.lrange(f"{CACHE_PREFIX}:blog_archive:{blog_id}", 0, -1)
    if len(blog_archive) == 0:
        return None
    elif blog_archive[0] == '-1':
        return []
    return blog_archive


@__try_redis(None)
def write_blog_archive_to_cache(blog_id: int, archive):
    cache_name = f"{CACHE_PREFIX}:blog_archive:{blog_id}"
    cache.delete(cache_name)
    if len(archive) == 0:
        cache.rpush(cache_name, -1)
    else:
        cache.rpush(cache_name, *archive)
    cache.expire(cache_name, CACHE_TIME)


@__try_redis(None)
def delete_blog_archive_from_cache(blog_id: int):
    cache.delete(f"{CACHE_PREFIX}:blog_archive:{blog_id}")


@__try_redis(None)
def delete_all_blog_archive_from_cache():
    for i in cache.keys(f"{CACHE_PREFIX}:blog_archive:*"):
        cache.delete(i)


@__try_redis(None)
def get_comment_from_cache(comment_id: int):
    comment = cache.hgetall(f"{CACHE_PREFIX}:comment:{comment_id}")
    if len(comment) != 4:
        return None
    return [comment.get("BlogID", ""),
            comment.get("Email", ""),
            comment.get("Content", ""),
            datetime.fromtimestamp(float(comment.get("UpdateTime", 0.0)))]


@__try_redis(None)
def write_comment_to_cache(comment_id: int, blog_id: str, email: str, content: str, update_time: str | datetime):
    cache_name = f"{CACHE_PREFIX}:comment:{comment_id}"
    cache.delete(cache_name)
    cache.hset(cache_name, mapping={
        "BlogID": blog_id,
        "Email": email,
        "Content": content,
        "UpdateTime": datetime.timestamp(update_time)
    })
    cache.expire(cache_name, CACHE_TIME)


@__try_redis(None)
def delete_comment_from_cache(comment_id: int):
    cache.delete(f"{CACHE_PREFIX}:comment:{comment_id}")


@__try_redis(None)
def get_user_comment_count_from_cache(user_id: int):
    count = cache.get(f"{CACHE_PREFIX}:comment_count:{user_id}")
    if count is not None:
        return int(count)


@__try_redis(None)
def write_user_comment_count_to_cache(user_id, count):
    cache_name = f"{CACHE_PREFIX}:comment_count:{user_id}"
    count = cache.set(cache_name, str(count))
    cache.expire(cache_name, CACHE_TIME)
    return count


@__try_redis(None)
def delete_user_comment_count_from_cache(user_id: int):
    cache.delete(f"{CACHE_PREFIX}:comment_count:{user_id}")


@__try_redis(None)
def delete_all_user_comment_count_from_cache():
    for i in cache.keys(f"{CACHE_PREFIX}:comment_count:*"):
        cache.delete(i)


@__try_redis(None)
def get_user_from_cache(email: str):
    user = cache.hgetall(f"{CACHE_PREFIX}:user:{email}")
    if len(user) != 3:
        return None
    return [user.get("PasswdHash", ""),
            int(user.get("Role", "")),
            int(user.get("ID", ""))]


@__try_redis(None)
def write_user_to_cache(email: str, passwd_hash: str, role: int, user_id: int):
    cache_name = f"{CACHE_PREFIX}:user:{email}"
    cache.delete(cache_name)
    cache.hset(cache_name, mapping={
        "PasswdHash": passwd_hash,
        "Role": role,
        "ID": user_id,
    })
    cache.expire(cache_name, CACHE_TIME)


@__try_redis(None)
def delete_user_from_cache(email: str):
    cache.delete(f"{CACHE_PREFIX}:user:{email}")


@__try_redis(None)
def get_user_email_from_cache(user_id: int):
    email = cache.get(f"{CACHE_PREFIX}:user_email:{user_id}")
    if email is None or len(email) == 0:
        return None
    return email


@__try_redis(None)
def write_user_email_to_cache(user_id: int, email: str):
    cache_name = f"{CACHE_PREFIX}:user_email:{user_id}"
    cache.set(cache_name, email)
    cache.expire(cache_name, CACHE_TIME)


@__try_redis(None)
def delete_user_email_from_cache(user_id: int):
    cache.delete(f"{CACHE_PREFIX}:user_email:{user_id}")


@__try_redis(None)
def get_role_name_from_cache(role_id: int):
    role_name = cache.get(f"{CACHE_PREFIX}:role_name:{role_id}")
    if role_name is None or len(role_name) == 0:
        return None
    return role_name


@__try_redis(None)
def write_role_name_to_cache(role_id: int, name: str):
    cache_name = f"{CACHE_PREFIX}:role_name:{role_id}"
    cache.set(cache_name, name)
    cache.expire(cache_name, CACHE_TIME)


@__try_redis(None)
def delete_role_name_from_cache(role_id: int):
    cache.delete(f"{CACHE_PREFIX}:role_name:{role_id}")


def get_role_operate_from_cache(role_id: int, operate: str):
    res = cache.get(f"{CACHE_PREFIX}:operate:{role_id}:{operate}")
    if res is None or len(res) == 0:
        return None
    return res == "True"


@__try_redis(None)
def write_role_operate_to_cache(role_id: int, operate: str, res: bool):
    cache_name = f"{CACHE_PREFIX}:operate:{role_id}:{operate}"
    cache.set(cache_name, str(res))
    cache.expire(cache_name, CACHE_TIME)


@__try_redis(None)
def delete_role_operate_from_cache(role_id: int):
    for i in cache.keys(f"{CACHE_PREFIX}:operate:{role_id}:*"):
        cache.delete(i)


@__try_redis(None)
def restart_clear_cache():
    """
    重启服务时必须要清理的缓存
    包括Hblog-Cache和Flask-Cache
    """

    # 删除全部Flask缓存
    for i in cache.keys("flask_cache:*"):
        cache.delete(i)
