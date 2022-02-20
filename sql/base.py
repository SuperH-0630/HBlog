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
        self.logger = logging.getLogger("mysql")
        self.logger.setLevel(conf["log-level"])
        if conf["log-home"] is not None:
            handle = logging.handlers.TimedRotatingFileHandler(
                os.path.join(conf["log-home"], f"mysql-{os.getpid()}-{name}@{host}.log"))
            handle.setFormatter(logging.Formatter(conf["log-format"]))
            self.logger.addHandler(handle)

    @abc.abstractmethod
    def close(self):
        """
        关闭数据库, 此代码执行后任何成员函数再被调用其行为是未定义的
        :return:
        """
        ...

    @abc.abstractmethod
    def is_connect(self) -> bool:
        """
        :return: 是否处于连接状态
        """
        ...

    @abc.abstractmethod
    def get_cursor(self) -> any:
        """
        :return: 返回数据库游标
        """
        ...

    @abc.abstractmethod
    def search(self, columns: List[str], table: str,
               where: Union[str, List[str]] = None,
               limit: Optional[int] = None,
               offset: Optional[int] = None,
               order_by: Optional[List[Tuple[str, str]]] = None):
        """
        执行 查询 SQL语句
        :param columns: 列名称
        :param table: 表
        :param where: 条件
        :param limit: 限制行数
        :param offset: 偏移
        :param order_by: 排序方式
        :return:
        """
        ...

    @abc.abstractmethod
    def insert(self, table: str, columns: list, values: Union[str, List[str]]):
        """
        执行 插入 SQL语句, 并提交
        :param table: 表
        :param columns: 列名称
        :param values: 数据
        :return:
        """
        ...

    @abc.abstractmethod
    def delete(self, table: str, where: Union[str, List[str]] = None):
        """
        执行 删除 SQL语句, 并提交
        :param table: 表
        :param where: 条件
        :return:
        """
        ...

    @abc.abstractmethod
    def update(self, table: str, kw: "Dict[str:str]", where: Union[str, List[str]] = None):
        """
        执行 更新 SQL语句, 并提交
        :param table: 表
        :param kw: 键值对
        :param where: 条件
        :return:
        """
        ...
