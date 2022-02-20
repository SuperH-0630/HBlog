# gunicorn.conf.py
import os
import multiprocessing
import logging.handlers
import logging

bind = '127.0.0.1:5000'
timeout = 30  # 超时

worker_class = 'gevent'
workers = multiprocessing.cpu_count() * 2 + 1  # 进程数
threads = 2  # 指定每个进程开启的线程数

hblog_path = os.path.join(os.environ['HOME'], "hblog")
os.makedirs(hblog_path, exist_ok=True, mode=0o775)

# 设置访问日志和错误信息日志路径
log_format = ("[%(levelname)s]:%(name)s:%(asctime)s "
              "(%(filename)s:%(lineno)d %(funcName)s) "
              "%(process)d %(thread)d "
              "%(message)s")
log_formatter = logging.Formatter(log_format)

# 错误日志
gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_error_logger.setLevel(logging.WARNING)

errorlog = os.path.join(hblog_path, "gunicorn_error.log")
time_handle = logging.handlers.TimedRotatingFileHandler(errorlog, when="d", backupCount=30, encoding='utf-8')
gunicorn_error_logger.addHandler(time_handle)
time_handle.setFormatter(log_formatter)

# 一般日志
gunicorn_access_logger = logging.getLogger("gunicorn.access")
gunicorn_access_logger.setLevel(logging.INFO)

accesslog = os.path.join(hblog_path, "gunicorn_access.log")
time_handle = logging.handlers.TimedRotatingFileHandler(accesslog, when="d", backupCount=10, encoding='utf-8')
gunicorn_access_logger.addHandler(time_handle)
time_handle.setFormatter(log_formatter)

# 输出日志
gunicorn_access_logger.info("Load gunicorn conf success")
gunicorn_access_logger.info(f"bind: {bind}")
gunicorn_access_logger.info(f"timeout: {timeout}")
gunicorn_access_logger.info(f"worker_class: {worker_class}")
gunicorn_access_logger.info(f"workers: {workers}")
gunicorn_access_logger.info(f"threads: {threads}")
gunicorn_access_logger.info(f"hblog_path: {hblog_path}")
