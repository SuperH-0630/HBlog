# gunicorn.conf.py
import os
import sys
import multiprocessing
import logging.handlers
import logging

bind = '0.0.0.0:80'
timeout = 30  # 超时

worker_class = 'gevent'
workers = multiprocessing.cpu_count() * 2 + 1  # 进程数
threads = 2  # 指定每个进程开启的线程数

loglevel = 'info'
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'

os.makedirs("~/hblog", exist_ok=True, mode=0o775)

# 设置访问日志和错误信息日志路径
log_format = ("[%(levelname)s] %(name)s %(asctime)s "
              "(%(pathname)s:%(lineno)d %(funcName)s) "
              "%(process)d %(thread)d "
              "%(message)s")
log_formatter = logging.Formatter(log_format)

console_handle = logging.StreamHandler(sys.stdout)
console_handle.setFormatter(log_formatter)

# 错误日志
gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_error_logger.setLevel(logging.WARNING)

gunicorn_error_logger.addHandler(console_handle)

errorlog = "~/hblog/gunicorn_error.log"
time_handle = logging.handlers.TimedRotatingFileHandler(errorlog, when="d", backupCount=30, encoding='utf-8')
gunicorn_error_logger.addHandler(time_handle)
time_handle.setFormatter(log_formatter)

# 一般日志
gunicorn_access_logger = logging.getLogger("gunicorn.access")
gunicorn_access_logger.setLevel(logging.INFO)

gunicorn_access_logger.addHandler(console_handle)

accesslog = "~/hblog/gunicorn_access.log"
time_handle = logging.handlers.TimedRotatingFileHandler(accesslog, when="d", backupCount=10, encoding='utf-8')
gunicorn_access_logger.addHandler(time_handle)
time_handle.setFormatter(log_formatter)
