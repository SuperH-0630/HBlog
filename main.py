from configure import configure, conf
import os
import logging

env_dict = os.environ
hblog_conf = env_dict.get("hblog_conf")
if hblog_conf is None:
    logging.info("Configure file ./etc/conf.json")
    configure("./etc/conf.json")
else:
    logging.info(f"Configure file {hblog_conf}")
    configure(hblog_conf)

from view import WebApp
from waitress import serve

web = WebApp(__name__)
app = web.get_app()

if conf["server-name"] is not None:
    app.config['SERVER_NAME'] = conf["server-name"]

if __name__ == '__main__':
    logging.info("Server start on 127.0.0.1:8080")
    serve(app, host='0.0.0.0', port="8080")
