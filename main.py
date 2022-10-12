from configure import configure
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

from app import HBlogFlask
from waitress import serve

app = HBlogFlask(__name__)
app.register_all_blueprint()

if __name__ == '__main__':
    logging.info("Server start on 127.0.0.1:8080")
    serve(app, host='0.0.0.0', port="8080")
