from configure import conf
import oss2
import logging.handlers
import logging
import os


class Aliyun:
    def __init__(self, key, secret, endpoint, name):
        self.key = key
        self.secret = secret
        self.auth = oss2.Auth(key, secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, name)
        self.logger = logging.getLogger("main.aliyun")
        self.logger.setLevel(conf["log-level"])
        if conf["log-home"] is not None:
            handle = logging.handlers.TimedRotatingFileHandler(
                os.path.join(conf["log-home"], f"aliyun-{os.getpid()}-{key}.log"))
            handle.setFormatter(logging.Formatter(conf["log-format"]))
            self.logger.addHandler(handle)

    def upload_file(self, name, f):
        res = self.bucket.put_object(name, f)
        self.logger.info(f"Upload {name} "
                         f"id: {res.request_id} status: {res.status} "
                         f"etag: {res.etag} resp: {res.resp} "
                         f"version id: {res.versionid} key: {self.key}")

    def shared_obj(self, name, time=15):
        url = self.bucket.sign_url('GET', name, time, slash_safe=True)
        self.logger.debug(f"Get url {url} name: {name} time: {time}s key: {self.key}")
        return url


if conf["aliyun"]:
    aliyun = Aliyun(conf["aliyun-key"],
                    conf["aliyun-secret"],
                    conf["aliyun-bucket-endpoint"],
                    conf["aliyun-bucket-name"])
else:
    aliyun = None
