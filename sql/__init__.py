from sql.mysql import MysqlDB
from configure import conf


DB = MysqlDB
db = DB(host=conf["MYSQL_URL"],
        name=conf["MYSQL_NAME"],
        passwd=conf["MYSQL_PASSWD"],
        port=conf["MYSQL_PORT"],
        database=conf["MYSQL_DATABASE"])
