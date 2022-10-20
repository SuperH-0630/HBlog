from configure import configure, conf

import os
import logging
import threading

env_dict = os.environ
hblog_conf = env_dict.get("hblog_conf")
if hblog_conf is None:
    logging.info("Configure file ./etc/conf.json")
    configure("./etc/conf.json")
else:
    logging.info(f"Configure file {hblog_conf}")
    configure(hblog_conf)

from app import HBlogFlask
from waitress import serve

app = HBlogFlask(__name__)
app.register_all_blueprint()

from sql.cache import restart_clear_cache
from sql.cache_refresh import refresh
restart_clear_cache()  # 清理缓存


@app.before_first_request
def before_first_requests():
    class FirstRefresh(threading.Thread):
        def __init__(self):
            super(FirstRefresh, self).__init__()
            self.daemon = True  # 设置为守护进程

        def run(self):
            refresh()

    class TimerRefresh(threading.Timer):
        def __init__(self):
            super(TimerRefresh, self).__init__(conf["CACHE_REFRESH_INTERVAL"], refresh)
            self.daemon = True  # 设置为守护进程

    FirstRefresh().start()
    TimerRefresh().start()


if __name__ == '__main__':
    logging.info("Server start on 127.0.0.1:8080")
    serve(app, host='0.0.0.0', port="8080")
