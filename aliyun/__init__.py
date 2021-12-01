from configure import conf
import oss2


class Aliyun:
    def __init__(self, key, secret, endpoint, name):
        self.key = key
        self.secret = secret
        self.auth = oss2.Auth(key, secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, name)

    def upload_file(self, name, f):
        self.bucket.put_object(name, f)

    def shared_obj(self, name, time=15):
        return self.bucket.sign_url('GET', name, time, slash_safe=True)


if conf["aliyun"]:
    aliyun = Aliyun(conf["aliyun-key"],
                    conf["aliyun-secret"],
                    conf["aliyun-bucket-endpoint"],
                    conf["aliyun-bucket-name"])
else:
    aliyun = None
