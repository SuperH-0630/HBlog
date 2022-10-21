from sql import redis
from configure import conf


PREFIX = conf["REDIS_PREFIX"]


def add_hello_click():
    redis.incr(f"{PREFIX}:home", amount=1)


def get_hello_click():
    res = redis.get(f"{PREFIX}:home")
    return res if res else 0


def add_home_click():
    redis.incr(f"{PREFIX}:index", amount=1)


def get_home_click():
    res = redis.get(f"{PREFIX}:index")
    return res if res else 0


def add_blog_click(blog_id: int):
    redis.incr(f"{PREFIX}:blog:{blog_id}", amount=1)


def get_blog_click(blog_id: int):
    res = redis.get(f"{PREFIX}:blog:{blog_id}")
    return res if res else 0


def add_archive_click(archive_id: int):
    redis.incr(f"{PREFIX}:archive:{archive_id}", amount=1)


def get_archive_click(archive_id: int):
    res = redis.get(f"{PREFIX}:archive:{archive_id}")
    return res if res else 0
