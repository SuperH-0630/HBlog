from sql.mysql import MysqlDB
from sql.redis import RedisDB
from configure import conf

DB = MysqlDB
db = DB(host=conf["MYSQL_URL"],
        name=conf["MYSQL_NAME"],
        passwd=conf["MYSQL_PASSWD"],
        port=conf["MYSQL_PORT"],
        database=conf["MYSQL_DATABASE"])

cache = redis.RedisDB(host=conf["CACHE_REDIS_HOST"],
                      port=conf["CACHE_REDIS_PORT"],
                      username=conf["CACHE_REDIS_NAME"],
                      passwd=conf["CACHE_REDIS_PASSWD"],
                      db=conf["CACHE_REDIS_DATABASE"])

redis = redis.RedisDB(host=conf["REDIS_HOST"],
                      port=conf["REDIS_PORT"],
                      username=conf["REDIS_NAME"],
                      passwd=conf["REDIS_PASSWD"],
                      db=conf["REDIS_DATABASE"])
