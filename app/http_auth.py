from flask import jsonify, g
from flask_httpauth import HTTPBasicAuth
from object.user import User


http_auth = HTTPBasicAuth()


@http_auth.verify_password
def verify_passwd(email, passwd):
    user = User(email)
    g.user = user
    return user.check_passwd(passwd)


@http_auth.error_handler
def unauthorized():
    rsp = jsonify({"status": 403, 'error': 'Unauthorized access'})
    rsp.status_code = 403
    return rsp
