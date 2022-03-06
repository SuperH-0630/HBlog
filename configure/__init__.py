import json
import logging
import os

conf = {
    "SECRET_KEY": "HBlog-R-Salt",
    "BLOG_NAME": "HBlog",
    "BLOG_DESCRIBE": "Huan Blog.",
    "FOOT": "Power by HBlog",
    "ABOUT_ME_NAME": "",
    "ABOUT_ME_DESCRIBE": "",
    "INTRODUCTION": "",
    "INTRODUCTION_LINK": "",
    "MYSQL_URL": "localhost",
    "MYSQL_NAME": "local",
    "MYSQL_PASSWD": "123456",
    "MYSQL_PORT": 3306,
    "MAIL_SERVER": "",
    "MAIL_PORT": "",
    "MAIL_TLS": False,
    "MAIL_SSL": False,
    "MAIL_PASSWD": "",
    "MAIL_PREFIX": "",
    "MAIL_SENDER": "",
    "USE_ALIYUN": False,
    "ALIYUN_KET": "",
    "ALIYUN_SECRET": "",
    "ALIYUN_BUCKET_ENDPOINT": "",
    "ALIYUN_BUCKET_NAME": "",
    "LOG_HOME": "",
    "LOG_FORMAT": "[%(levelname)s]:%(name)s:%(asctime)s "
                  "(%(filename)s:%(lineno)d %(funcName)s) "
                  "%(process)d %(thread)d "
                  "%(message)s",
    "LOG_LEVEL": logging.INFO,
    "LOG_STDERR": True,
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
