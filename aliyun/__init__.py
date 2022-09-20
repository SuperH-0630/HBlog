from configure import conf
import oss2
import logging.handlers
import logging
import os
from urllib.parse import urljoin


class Aliyun:
    def __init__(self, key, secret, endpoint, name, is_cname):
        self.key = key
        self.secret = secret
        self.auth = oss2.Auth(key, secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, name, is_cname=is_cname)
        self.logger = logging.getLogger("main.aliyun")
        self.logger.setLevel(conf["LOG_LEVEL"])
        if len(conf["LOG_HOME"]) > 0:
            handle = logging.handlers.TimedRotatingFileHandler(
                os.path.join(conf["LOG_HOME"], f"aliyun.log"), backupCount=10)
            handle.setFormatter(logging.Formatter(conf["LOG_FORMAT"]))
            self.logger.addHandler(handle)

    def upload_file(self, name, f):
        res = self.bucket.put_object(name, f)
        self.logger.info(f"Upload {name} "
                         f"id: {res.request_id} status: {res.status} "
                         f"etag: {res.etag} resp: {res.resp} "
                         f"version id: {res.versionid} key: {self.key}")

    def shared_obj(self, name, time=15):
        if not self.bucket.object_exists(name):
            return None
        if conf["ALIYUN_BUCKET_USE_SIGN_URL"]:
            url = self.bucket.sign_url('GET', name, time, slash_safe=True)
        else:
            url = urljoin(conf["ALIYUN_BUCKET_ENDPOINT"], name)
        self.logger.debug(f"Get url {url} name: {name} time: {time}s key: {self.key}")
        return url


if conf["USE_ALIYUN"]:
    aliyun = Aliyun(conf["ALIYUN_KEY"],
                    conf["ALIYUN_SECRET"],
                    conf["ALIYUN_BUCKET_ENDPOINT"],
                    conf["ALIYUN_BUCKET_NAME"],
                    conf["ALIYUN_BUCKET_IS_CNAME"])
else:
    aliyun = None
