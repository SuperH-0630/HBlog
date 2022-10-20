from sql import DB
from configure import conf
from sql.archive import read_archive, get_archive_list_iter, get_blog_archive
from sql.blog import read_blog, get_blog_count, get_archive_blog_count, get_user_blog_count, get_blog_list_iter
from sql.comment import read_comment, read_comment_list_iter, get_user_comment_count
from sql.msg import read_msg, read_msg_list_iter, get_msg_count, get_user_msg_count
from sql.user import (read_user, get_user_list_iter, get_role_list_iter,
                      get_user_email, get_role_name, check_role, role_authority)
import logging.handlers
import os

refresh_logger = logging.getLogger("main.refresh")
refresh_logger.setLevel(conf["LOG_LEVEL"])
if len(conf["LOG_HOME"]) > 0:
    handle = logging.handlers.TimedRotatingFileHandler(
        os.path.join(conf["LOG_HOME"], f"redis-refresh.log"), backupCount=10)
    handle.setFormatter(logging.Formatter(conf["LOG_FORMAT"]))
    refresh_logger.addHandler(handle)


def refresh():
    mysql = DB(host=conf["MYSQL_URL"],
               name=conf["MYSQL_NAME"],
               passwd=conf["MYSQL_PASSWD"],
               port=conf["MYSQL_PORT"],
               database=conf["MYSQL_DATABASE"])

    refresh_logger.info("refresh redis cache started.")

    for i in get_archive_list_iter():
        read_archive(i[0], mysql, not_cache=True)
        get_archive_blog_count(i[0], mysql, not_cache=True)

    for i in get_blog_list_iter():
        read_blog(i[0], mysql, not_cache=True)
        get_blog_archive(i[0], mysql, not_cache=True)
    get_blog_count(mysql, not_cache=True)

    for i in read_comment_list_iter():
        read_comment(i[0], mysql, not_cache=True)

    for i in read_msg_list_iter():
        read_msg(i[0], mysql, not_cache=True)
    get_msg_count(mysql, not_cache=True)

    for i in get_user_list_iter():
        email = get_user_email(i[0], mysql, not_cache=True)
        get_user_blog_count(i[0], mysql, not_cache=True)
        get_user_comment_count(i[0], mysql, not_cache=True)
        get_user_msg_count(i[0], mysql, not_cache=True)
        read_user(email, mysql, not_cache=True)

    for i in get_role_list_iter():
        get_role_name(i[0], mysql, not_cache=True)
        for a in role_authority:
            check_role(i[0], a, mysql, not_cache=True)

    refresh_logger.info("refresh redis cache finished.")
