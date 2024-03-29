import abc
from typing import List, Dict, Tuple, Union, Optional
import logging.handlers
import logging
from configure import conf
import os


class DBException(Exception):
    ...


class DBDoneException(DBException):
    ...


class DBCloseException(DBException):
    ...


class DBBit:
    BIT_0 = b'\x00'
    BIT_1 = b'\x01'


class Database(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, host: str, name: str, passwd: str, port: str):
        self._host = str(host)
        self._name = str(name)
        self._passwd = str(passwd)
        if port is None:
            self._port = 3306
        else:
            self._port = int(port)
        self.logger = logging.getLogger("main.database")
        self.logger.setLevel(conf["LOG_LEVEL"])
        if len(conf["LOG_HOME"]) > 0:
            handle = logging.handlers.TimedRotatingFileHandler(
                os.path.join(conf["LOG_HOME"], f"mysql-{name}@{host}.log"), backupCount=10)
            handle.setFormatter(logging.Formatter(conf["LOG_FORMAT"]))
            self.logger.addHandler(handle)

    @abc.abstractmethod
    def search(self, sql: str, *args, not_commit: bool = False):
        """
        执行 查询 SQL语句
        :parm sql: SQL语句
        :return:
        """
        ...

    @abc.abstractmethod
    def insert(self, sql: str, *args, not_commit: bool = False):
        """
        执行 插入 SQL语句, 并提交
        :parm sql: SQL语句
        :return:
        """
        ...

    @abc.abstractmethod
    def delete(self, sql: str, *args, not_commit: bool = False):
        """
        执行 删除 SQL语句, 并提交
        :parm sql: SQL语句
        :return:
        """
        ...

    @abc.abstractmethod
    def update(self, sql: str, *args, not_commit: bool = False):
        """
        执行 更新 SQL语句, 并提交
        :parm sql: SQL语句
        :return:
        """
        ...
