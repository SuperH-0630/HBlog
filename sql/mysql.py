import pymysql.cursors
import pymysql
import threading
from sql.base import Database, DBException, DBCloseException
from typing import Optional, Union, List, Tuple, Dict


class MysqlConnectException(DBCloseException):
    """Mysql Connect error"""


class MysqlDB(Database):
    def __init__(self,
                 host: Optional[str],
                 name: Optional[str],
                 passwd: Optional[str],
                 port: Optional[str]):
        if host is None or name is None:
            raise DBException
        super(MysqlDB, self).__init__(host=host, name=name, passwd=passwd, port=port)
        try:
            self._db = pymysql.connect(user=self._name,
                                       password=self._passwd,
                                       host=self._host,
                                       port=self._port,
                                       database="HBlog")
        except pymysql.err.OperationalError:
            raise
        self._cursor = self._db.cursor()
        self._lock = threading.RLock()
        self.logger.info(f"MySQL({self._name}@{self._host}) connect")

    def close(self):
        self._close()

    def is_connect(self) -> bool:
        if self._cursor is None or self._db is None:
            return False

        try:
            self._db.ping(False)
        except Exception:
            return False
        else:
            return True

    def get_cursor(self) -> pymysql.cursors.Cursor:
        if self._cursor is None or self._db is None:
            raise DBCloseException
        return self._cursor

    def search(self, columns: List[str], table: str,
               where: Union[str, List[str]] = None,
               limit: Optional[int] = None,
               offset: Optional[int] = None,
               order_by: Optional[List[Tuple[str, str]]] = None,
               group_by: Optional[List[str]] = None,
               for_update: bool = False) -> Union[None, pymysql.cursors.Cursor]:
        if type(where) is list and len(where) > 0:
            where: str = " WHERE " + " AND ".join(f"({w})" for w in where)
        elif type(where) is str and len(where) > 0:
            where = " WHERE " + where
        else:
            where: str = ""

        if order_by is None:
            order_by: str = ""
        else:
            by = [f" {i[0]} {i[1]} " for i in order_by]
            order_by: str = " ORDER BY" + ", ".join(by)

        if limit is None or limit == 0:
            limit: str = ""
        else:
            limit = f" LIMIT {limit}"

        if offset is None:
            offset: str = ""
        else:
            offset = f" OFFSET {offset}"

        if group_by is None:
            group_by: str = ""
        else:
            group_by = "GROUP BY " + ", ".join(group_by)

        columns: str = ", ".join(columns)
        if for_update:
            for_update = "FOR UPDATE"
        else:
            for_update = ""
        return self.__search(f"SELECT {columns} "
                             f"FROM {table} "
                             f"{where} {group_by} {order_by} {limit} {offset} {for_update};")

    def insert(self, table: str, columns: list, values: Union[str, List[str]],
               not_commit: bool = False) -> Union[None, pymysql.cursors.Cursor]:
        columns: str = ", ".join(columns)
        if type(values) is str:
            values: str = f"({values})"
        else:
            values: str = ", ".join(f"{v}" for v in values)
        return self.__done(f"INSERT INTO {table}({columns}) VALUES {values};", not_commit=not_commit)

    def delete(self, table: str, where: Union[str, List[str]] = None,
               not_commit: bool = False) -> Union[None, pymysql.cursors.Cursor]:
        if type(where) is list and len(where) > 0:
            where: str = " AND ".join(f"({w})" for w in where)
        elif type(where) is not str or len(where) == 0:  # 必须指定条件
            return None

        return self.__done(f"DELETE FROM {table} WHERE {where};", not_commit=not_commit)

    def update(self, table: str, kw: "Dict[str:str]", where: Union[str, List[str]] = None,
               not_commit: bool = False) -> Union[None, pymysql.cursors.Cursor]:
        if len(kw) == 0:
            return None

        if type(where) is list and len(where) > 0:
            where: str = " AND ".join(f"({w})" for w in where)
        elif type(where) is not str or len(where) == 0:  # 必须指定条件
            return None

        kw_list = [f"{key} = {kw[key]}" for key in kw]
        kw_str = ", ".join(kw_list)
        return self.__done(f"UPDATE {table} SET {kw_str} WHERE {where};", not_commit=not_commit)

    def commit(self):
        self._commit()

    def __search(self, sql) -> Union[None, pymysql.cursors.Cursor]:
        try:
            self._lock.acquire()  # 上锁
            self._connect()
            self._cursor.execute(sql)
        except pymysql.MySQLError:
            self.logger.error(f"MySQL({self._name}@{self._host}) SQL {sql} error", exc_info=True, stack_info=True)
            return None
        finally:
            self._lock.release()  # 释放锁
        return self._cursor

    def __done(self, sql, not_commit: bool = False) -> Union[None, pymysql.cursors.Cursor]:
        try:
            self._lock.acquire()
            self._connect()
            self._cursor.execute(sql)
        except pymysql.MySQLError:
            self._db.rollback()
            self.logger.error(f"MySQL({self._name}@{self._host}) SQL {sql} error", exc_info=True, stack_info=True)
            return None
        finally:
            if not not_commit:
                self._db.commit()
            self._lock.release()
        return self._cursor

    def _connect(self):
        if self._db is None:
            raise MysqlConnectException

        try:
            self._db.ping(False)
        except Exception:
            raise MysqlConnectException

    def _close(self):
        if self._cursor is not None:
            self._cursor.close()
        if self._db is not None:
            self._db.close()
        self._db = None
        self._cursor = None
        self._lock = None
        self.logger.warning(f"MySQL({self._name}@{self._host}) connect close")

    def _commit(self):
        try:
            self._lock.acquire()
            self._connect()
            self._db.commit()
        except pymysql.MySQLError:
            self.logger.error(f"MySQL({self._name}@{self._host}) commit error", exec_info=True)
        finally:
            self._lock.release()
