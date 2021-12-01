import json

with open("conf.json", encoding='utf-8') as f:
    json_str = f.read()
    _conf: dict = json.loads(json_str)


conf = dict()

_mysql = _conf["mysql"]
conf["mysql_url"] = str(_mysql["url"])
conf["mysql_name"] = str(_mysql["name"])
conf["mysql_passwd"] = str(_mysql["passwd"])
conf["mysql_port"] = int(_mysql.get("port", 3306))

_email = _conf["email"]
conf["email_server"] = str(_email["server"])
conf["email_port"] = int(_email["port"])
conf["email_tls"] = bool(_email.get("tls", False))
conf["email_ssl"] = bool(_email.get("ssl", False))
conf["email_name"] = str(_email["name"])
conf["email_passwd"] = str(_email["passwd"])
conf["email_prefix"] = str(_email.get("prefix", "[HBlog]"))
conf["email_sender"] = str(_email["sender"])

conf["secret-key"] = str(_conf.get("secret-key", "HBlog-R-Salt"))

introduce = _conf["info"]["introduce"]
introduce_list = []
for i in introduce:
    describe: str = introduce[i]
    describe = " ".join([f"<p>{i}</p>" for i in describe.split('\n')])
    introduce_list.append((i, describe))

conf["describe-link"] = _conf["info"]["link"]
conf["describe-info"] = introduce_list

conf["blog-name"] = _conf["info"]["blog-name"]
conf["blog-describe"] = _conf["info"]["blog-describe"]

conf["about-me-name"] = _conf["info"]["about-me"]["name"]
conf["about-me-describe"] = _conf["info"]["about-me"]["describe"]

conf["about-me-project"] = _conf["info"]["project"]
conf["about-me-skill"] = _conf["info"]["skill"]
conf["about-me-read"] = _conf["info"]["read"]

conf["foot-info"] = f'{_conf["info"]["foot-info"]} Power by HBlog'

aliyun = _conf.get("aliyun")
if aliyun is None:
    conf["aliyun"] = False
else:
    conf["aliyun"] = True
    conf["aliyun-key"] = aliyun["Key"]
    conf["aliyun-secret"] = aliyun["Secret"]
    conf["aliyun-bucket-endpoint"] = aliyun["Bucket-Endpoint"]
    conf["aliyun-bucket-name"] = aliyun["Bucket-Name"]
