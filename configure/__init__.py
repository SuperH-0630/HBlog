import json
import logging
import os

conf = {
    "DEBUG_PROFILE": False,
    "SECRET_KEY": "HBlog-R-Salt",
    "BLOG_NAME": "HBlog",
    "BLOG_DESCRIBE": "Huan Blog.",
    "FOOT": "Power by HBlog",
    "ABOUT_ME_PAGE": "",
    "INTRODUCTION": "",
    "INTRODUCTION_LINK": "",
    "MYSQL_URL": "localhost",
    "MYSQL_NAME": "localhost",
    "MYSQL_PASSWD": "123456",
    "MYSQL_PORT": 3306,
    "MYSQL_DATABASE": "HBlog",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_NAME": "localhost",
    "REDIS_PASSWD": "123456",
    "REDIS_DATABASE": 0,
    "REDIS_EXPIRE": 604800,  # 默认七天过期
    "MAIL_SERVER": "",
    "MAIL_PORT": "",
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": False,
    "MAIL_PASSWORD": "",
    "MAIL_USERNAME": "",
    "MAIL_PREFIX": "",
    "MAIL_SENDER": "",
    "USE_ALIYUN": False,
    "ALIYUN_KEY": "",
    "ALIYUN_SECRET": "",
    "ALIYUN_BUCKET_ENDPOINT": "",
    "ALIYUN_BUCKET_NAME": "",
    "ALIYUN_BUCKET_IS_CNAME": False,
    "ALIYUN_BUCKET_USE_SIGN_URL": True,
    "LOG_HOME": "",
    "LOG_FORMAT": "[%(levelname)s]:%(name)s:%(asctime)s "
                  "(%(filename)s:%(lineno)d %(funcName)s) "
                  "%(process)d %(thread)d "
                  "%(message)s",
    "LOG_LEVEL": logging.INFO,
    "LOG_STDERR": True,
    "LOGO": "logo.jpg",
    "ICP": None,
    "GONG_AN": None,
}


def configure(conf_file: str, encoding="utf-8"):
    """ 运行配置程序, 该函数需要在其他模块被执行前调用 """
    with open(conf_file, mode="r", encoding=encoding) as f:
        json_str = f.read()
        conf.update(json.loads(json_str))
    if type(conf["LOG_LEVEL"]) is str:
        conf["LOG_LEVEL"] = {"debug": logging.DEBUG,
                             "info": logging.INFO,
                             "warning": logging.WARNING,
                             "error": logging.ERROR}.get(conf["LOG_LEVEL"])

    introduce = conf["INTRODUCE"]
    introduce_list = []
    for i in introduce:
        describe: str = introduce[i]
        describe = " ".join([f"<p>{i}</p>" for i in describe.split('\n')])
        introduce_list.append((i, describe))
    conf["INTRODUCE"] = introduce_list
    if len(conf["LOG_HOME"]) > 0:
        os.makedirs(conf["LOG_HOME"], exist_ok=True)
