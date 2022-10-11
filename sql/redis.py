import redis
import logging
import logging.handlers
from configure import conf
import os


class RedisDB(redis.StrictRedis):
    def __init__(self, host, port, username, passwd, db):
        super().__init__(host=host, port=port, username=username, password=passwd, db=db, decode_responses=True)

        # redis是线程安全的

        self.logger = logging.getLogger("main.database")
        self.logger.setLevel(conf["LOG_LEVEL"])
        if len(conf["LOG_HOME"]) > 0:
            handle = logging.handlers.TimedRotatingFileHandler(
                os.path.join(conf["LOG_HOME"], f"redis-{username}@{host}.log"), backupCount=10)
            handle.setFormatter(logging.Formatter(conf["LOG_FORMAT"]))
            self.logger.addHandler(handle)
