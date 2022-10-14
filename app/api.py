from flask import Blueprint, jsonify, request, abort, g
from configure import conf
from json import loads
from datetime import datetime

from object.archive import Archive
from object.blog import BlogArticle
from object.msg import Message
from object.comment import Comment
from object.user import User

from app.http_auth import http_auth
from app.tool import api_role_required


api = Blueprint("api", __name__)


@api.route("/", methods=["GET", "POST"])
def api_say_hello():
    json = loads(request.get_json())
    name = "unknown"
    if json:
        name = json.get("name", "unknown")
    res = {"status": 200, name: "Hello!"}
    return res


@api.route("/get_introduce")
@http_auth.login_required
def api_get_introduce():
    title = request.args.get("title").lower()

    res = {"status": 200, "introduce": {}}
    have_found = False
    for info in conf['INTRODUCE']:
        if title is None or title == info[0].lower():
            res["introduce"][info[0]] = info[1]
            have_found = True

    if not have_found:
        abort(404)
    return jsonify(res)


@api.route("/find_me")
@http_auth.login_required
def api_get_find_me():
    where = request.args.get("where")
    if where:
        where = where.lower()

    res = {"status": 200, "content": {}}
    have_found = False
    for i in conf['INTRODUCE_LINK']:
        if where is None or where == i.lower():
            res["content"][i] = conf['INTRODUCE_LINK'][i]
            have_found = True

    if not have_found:
        abort(404)
    return jsonify(res)


@api.route("/archive_list")
@http_auth.login_required
@api_role_required("ReadBlog", "api get archive list")
def api_get_archive_list():
    archive_list = Archive.get_archive_list()
    res = {"status": 200}
    res_list = []
    for i in archive_list:
        res_list.append({
            "name": i.name,
            "describe": i.describe,
            "count": i.count,
            "id": i.id,
        })

    res["archive"] = res_list
    return jsonify(res)


@api.route("/archive/<int:archive_id>")
@http_auth.login_required
@api_role_required("ReadBlog", "api get archive")
def get_get_archive(archive_id):
    archive = Archive(archive_id)
    if len(archive.name) == 0:
        abort(404)
    return {
        "status": 200,
        "archive": {
            "name": archive.name,
            "describe": archive.describe,
            "count": archive.count,
            "id": archive.id,
        }
    }


@api.route("/archive_blog_list/<int:archive_id>/<int:page>")
@http_auth.login_required
@api_role_required("ReadBlog", "api get archive blog list")
def api_get_archive_blog_list(archive_id: int, page: int):
    blog_list = BlogArticle.get_blog_list(archive_id=archive_id, limit=20, offset=(page - 1) * 20)
    res = {"status": 200}
    res_list = []
    for i in blog_list:
        res_list.append({
            "auth": i.user.id,
            "title": i.title,
            "subtitle": i.subtitle,
            "update_time": datetime.timestamp(i.update_time),
            "create_time": datetime.timestamp(i.create_time),
            "top": i.top,
            "id": i.id,
        })

    res["blog"] = res_list
    return jsonify(res)


@api.route("/blog_list/<int:page>")
@http_auth.login_required
@api_role_required("ReadBlog", "api get blog list")
def api_get_blog_list(page: int):
    blog_list = BlogArticle.get_blog_list(limit=20, offset=(page - 1) * 20)
    res = {"status": 200}
    res_list = []
    for i in blog_list:
        res_list.append({
            "auth": i.user.id,
            "title": i.title,
            "subtitle": i.subtitle,
            "update_time": datetime.timestamp(i.update_time),
            "create_time": datetime.timestamp(i.create_time),
            "top": i.top,
            "id": i.id,
        })

    res["blog"] = res_list
    return jsonify(res)



@api.route("/blog/<int:blog_id>")
@http_auth.login_required
@api_role_required("ReadBlog", "api get blog")
def api_get_blog(blog_id: int):
    blog = BlogArticle(blog_id)
    return {
        "status": 200,
        "blog": {
            "auth": blog.user.id,
            "title": blog.title,
            "subtitle": blog.subtitle,
            "update_time": datetime.timestamp(blog.update_time),
            "create_time": datetime.timestamp(blog.create_time),
            "top": blog.top,
            "content": blog.content,
            "id": blog.id,
        }
    }


@api.route("/get_blog_comment/<int:blog_id>")
@http_auth.login_required
@api_role_required("ReadComment", "api get blog comment")
def api_get_blog_comment(blog_id: int):
    blog = BlogArticle(blog_id)
    res = {"status": 200}
    res_list = []
    for i in blog.comment:
        res_list.append({
            "auth": i.auth.id,
            "update_time": datetime.timestamp(i.update_time),
            "id": i.id,
        })

    res["comment"] = res_list
    return jsonify(res)


@api.route("/comment/<int:comment_id>")
@http_auth.login_required
@api_role_required("ReadComment", "api get comment")
def api_get_comment(comment_id: int):
    comment = Comment(comment_id)
    return {
        "status": 200,
        "blog": {
            "auth": comment.auth.id,
            "update_time": datetime.timestamp(comment.update_time),
            "content": comment.content,
            "id": comment.id,
        }
    }


@api.route("/msg_list/<int:page>")
@http_auth.login_required
@api_role_required("ReadMsg", "api get msg list")
def api_get_not_secret_msg_list(page: int):
    msg_list = Message.get_message_list(20, (page - 1) * 20, request.args.get("secret", False))
    res = {"status": 200}
    res_list = []
    for i in msg_list:
        res_list.append({
            "auth": i.auth.id,
            "update_time": datetime.timestamp(i.update_time),
            "id": i.id,
        })

    res["blog"] = res_list
    return jsonify(res)


@api.route("/s_msg_list/<int:page>")
@http_auth.login_required
@api_role_required("ReadMsg", "api get all msg secret list")
@api_role_required("ReadSecretMsg", "api get all secret list")
def api_get_secret_msg_list(page: int):
    msg_list = Message.get_message_list(20, (page - 1) * 20, request.args.get("secret", True))
    res = {"status": 200}
    res_list = []
    for i in msg_list:
        res_list.append({
            "auth": i.auth.id,
            "update_time": datetime.timestamp(i.update_time),
            "id": i.id,
        })

    res["blog"] = res_list
    return jsonify(res)


@api.route("/msg/<int:msg_id>")
@http_auth.login_required
@api_role_required("ReadMsg", "api get msg")
def api_get_msg(msg_id: int):
    msg = Message(msg_id)
    if msg.secret:
        abort(404)
    return {
        "status": 200,
        "blog": {
            "auth": msg.auth.id,
            "update_time": datetime.timestamp(msg.update_time),
            "content": msg.content,
            "id": msg.id,
        }
    }


@api.route("/s_msg/<int:msg_id>")
@http_auth.login_required
@api_role_required("ReadMsg", "api get secret msg")
@api_role_required("ReadSecretMsg", "api get secret msg")
def api_get_secret_msg(msg_id: int):
    msg = Message(msg_id)
    return {
        "status": 200,
        "blog": {
            "auth": msg.auth.id,
            "update_time": datetime.timestamp(msg.update_time),
            "content": msg.content,
            "id": msg.id,
        }
    }


@api.route("/user/<int:user_id>")
@http_auth.login_required
@api_role_required("ReadUserInfo", "api get user info")
def api_get_user(user_id: int):
    user = User(user_id, is_id=True)
    return {
        "status": 200,
        "blog": {
            "role": user.role,
            "email": user.email,
            "id": user.id,
        }
    }

