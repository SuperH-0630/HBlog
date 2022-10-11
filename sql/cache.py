from sql import cache

from redis import RedisError
from functools import wraps
from datetime import datetime


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
def read_msg_from_cache(msg_id: int):
    msg = cache.hgetall(f"cache:msg:{msg_id}")
    if len(msg) != 4:
        return None
    return [msg.get("Email", ""),
            msg.get("Content"),
            datetime.fromisoformat(msg.get("UpdateTime", "2022-1-1 00:00:00")),
            bool(msg.get("Secret", False))]


@__try_redis(None)
def write_msg_to_cache(msg_id: int, email: str, content: str, update_time: str | datetime, secret: bool):
    cache_name = f"cache:msg:{msg_id}"
    cache.delete(cache_name)
    cache.hset(cache_name, mapping={
        "Email": email,
        "Content": content,
        "UpdateTime": str(update_time),
        "Secret": str(secret)
    })
    cache.expire(cache_name, 3600)


@__try_redis(None)
def delete_msg_from_cache(msg_id: int):
    cache.delete(f"cache:msg:{msg_id}")


@__try_redis(None)
def get_msg_cout_from_cache():
    count = cache.get("cache:msg_count")
    if count is not None:
        return int(count)


@__try_redis(None)
def write_msg_count_to_cache(count):
    count = cache.set("cache:msg_count", str(count))
    cache.expire("cache:msg_count", 3600)
    return count


@__try_redis(None)
def delete_msg_count_from_cache():
    cache.delete("cache:msg_count")


@__try_redis(None)
def get_user_msg_count_from_cache(user_id: int):
    count = cache.get(f"cache:msg_count:{user_id}")
    if count is not None:
        return int(count)


@__try_redis(None)
def write_user_msg_count_to_cache(user_id, count):
    cache_name = f"cache:msg_count:{user_id}"
    count = cache.set(cache_name, str(count))
    cache.expire(cache_name, 3600)
    return count


@__try_redis(None)
def delete_all_user_msg_count_from_cache():
    for i in cache.keys("cache:msg_count:*"):
        cache.delete(i)


@__try_redis(None)
def read_blog_from_cache(blog_id: int):
    blog = cache.hgetall(f"cache:blog:{blog_id}")
    if len(blog) != 4:
        return None
    return [int(blog.get("Auth", -1)),
            blog.get("Title"),
            blog.get("SubTitle"),
            blog.get("Content"),
            datetime.fromisoformat(blog.get("UpdateTime", "2022-1-1 00:00:00")),
            datetime.fromisoformat(blog.get("CreateTime", "2022-1-1 00:00:00")),
            bool(blog.get("Top", False))]


@__try_redis(None)
def write_blog_to_cache(blog_id: int, auth_id: str, title: str, subtitle: str, content: str,
                        update_time: str | datetime, create_time: str | datetime, top: bool):
    cache_name = f"cache:blog:{blog_id}"
    cache.delete(cache_name)
    cache.hset(cache_name, mapping={
        "Auth": auth_id,
        "Title": title,
        "SubTitle": subtitle,
        "Content": content,
        "UpdateTime": str(update_time),
        "CreateTime": str(create_time),
        "Top": str(top)
    })
    cache.expire(cache_name, 3600)


@__try_redis(None)
def delete_blog_from_cache(blog_id: int):
    cache.delete(f"cache:blog:{blog_id}")


@__try_redis(None)
def get_blog_count_from_cache():
    count = cache.get("cache:blog_count")
    if count is not None:
        return int(count)
    return


@__try_redis(None)
def write_blog_count_to_cache(count):
    count = cache.set("cache:blog_count", str(count))
    cache.expire("cache:blog_count", 3600)
    return count


@__try_redis(None)
def delete_blog_count_from_cache():
    cache.delete("cache:blog_count")


@__try_redis(None)
def get_archive_blog_count_from_cache(archive_id: int):
    count = cache.get(f"cache:blog_count:archive:{archive_id}")
    if count is not None:
        return int(count)


@__try_redis(None)
def write_archive_blog_count_to_cache(archive_id, count):
    cache_name = f"cache:blog_count:archive:{archive_id}"
    count = cache.set(cache_name, str(count))
    cache.expire(cache_name, 3600)
    return count


@__try_redis(None)
def delete_all_archive_blog_count_from_cache():
    for i in cache.keys("cache:blog_count:archive:*"):
        cache.delete(i)


@__try_redis(None)
def delete_archive_blog_count_from_cache(archive_id: int):
    cache.delete(f"cache:blog_count:archive:{archive_id}")


@__try_redis(None)
def get_user_blog_count_from_cache(user_id: int):
    count = cache.get(f"cache:blog_count:user:{user_id}")
    if count is not None:
        return int(count)


@__try_redis(None)
def write_user_blog_count_to_cache(user_id, count):
    cache_name = f"cache:blog_count:user:{user_id}"
    count = cache.set(cache_name, str(count))
    cache.expire(cache_name, 3600)
    return count


@__try_redis(None)
def delete_all_user_blog_count_from_cache():
    for i in cache.keys("cache:blog_count:user:*"):
        cache.delete(i)


@__try_redis(None)
def delete_user_blog_count_from_cache(user_id: int):
    cache.delete(f"cache:blog_count:user:{user_id}")
