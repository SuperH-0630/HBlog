from sql.mysql import MysqlDB
from configure import conf


DB = MysqlDB
db = DB(host=conf["mysql_url"], name=conf["mysql_name"], passwd=conf["mysql_passwd"], port=conf["mysql_port"])
