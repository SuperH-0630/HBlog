import pymysql
from dbutils.pooled_db import PooledDB
from dbutils.steady_db import SteadyDBCursor
from sql.base import Database, DBException, DBCloseException
from typing import Optional, Union
import inspect


class MysqlConnectException(DBCloseException):
    """Mysql Connect error"""


class MysqlDB(Database):
    class Result:
        def __init__(self, cur: SteadyDBCursor):
            self.res: list = cur.fetchall()
            self.lastrowid: int = cur.lastrowid
            self.rowcount: int = cur.rowcount

        def fetchall(self):
            return self.res

        def fetchone(self):
            return self.res[0]

        def __iter__(self):
            return self.res.__iter__()

    class Connection:
        def __init__(self, conn):
            self.conn = conn
            self.cur = conn.cursor()

        def get_cursor(self):
            return self.cur

        def commit(self):
            self.conn.commit()

        def rollback(self):
            self.conn.rollback()

        def close(self):
            self.cur.close()
            self.conn.close()


    def __init__(self,
                 host: Optional[str],
                 name: Optional[str],
                 passwd: Optional[str],
                 port: Optional[str],
                 database: str = "HBlog"):
        if host is None or name is None:
            raise DBException

        super(MysqlDB, self).__init__(host=host, name=name, passwd=passwd, port=port)
        self.database = database

        self.pool = PooledDB(pymysql,
                             mincached=1,
                             maxcached=4,
                             maxconnections=16,
                             blocking=True,
                             host=self._host,
                             port=self._port,
                             user=self._name,
                             passwd=self._passwd,
                             db=self.database)

        self.logger.info(f"MySQL({self._name}@{self._host}) connect")

    def get_connection(self):
        return MysqlDB.Connection(self.pool.connection())

    def search(self, sql: str, *args) -> Union[None, Result]:
        return self.__search(sql, args)

    def insert(self, sql: str, *args, connection: Connection = None) -> Union[None, Result]:
        return self.__done(sql, args, connection)

    def delete(self, sql: str, *args, connection: Connection = None) -> Union[None, Result]:
        return self.__done(sql, args, connection)

    def update(self, sql: str, *args, connection: Connection = None) -> Union[None, Result]:
        return self.__done(sql, args, connection)

    def __search(self, sql, args) -> Union[None, Result]:
        conn = self.pool.connection()
        cur = conn.cursor()

        try:
            cur.execute(query=sql, args=args)
        except pymysql.MySQLError:
            self.logger.error(f"MySQL({self._name}@{self._host}) SQL {sql} with {args} error {inspect.stack()[2][2]} "
                              f"{inspect.stack()[2][1]} {inspect.stack()[2][3]}", exc_info=True, stack_info=True)
            return None
        else:
            return MysqlDB.Result(cur)
        finally:
            cur.close()
            conn.close()

    def __done(self, sql, args, connection: Connection = None) -> Union[None, Result]:
        if connection:
            cur = connection.get_cursor()
            conn = None
        else:
            conn = self.pool.connection()
            cur = conn.cursor()

        try:
            cur.execute(query=sql, args=args)
            if conn:
                conn.commit()
        except pymysql.MySQLError:
            if conn:
                conn.rollback()
            self.logger.error(f"MySQL({self._name}@{self._host}) SQL {sql} error {inspect.stack()[2][2]} "
                              f"{inspect.stack()[2][1]} {inspect.stack()[2][3]}", exc_info=True, stack_info=True)
            return None
        else:
            return MysqlDB.Result(cur)
        finally:
            if not connection:
                cur.close()
                conn.close()
