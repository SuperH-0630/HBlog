from flask import Blueprint, render_template, abort, redirect, url_for, flash, make_response
from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from flask_login import login_required, current_user
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired
import bleach
from markdown import markdown

import app
from sql.base import DBBit
from object.blog import BlogArticle, load_blog_by_id
from object.user import User
from object.comment import Comment
from object.archive import load_archive_by_name

docx = Blueprint("docx", __name__)
allow_tag = ['a', 'abbr', 'acronym', 'b', 'br', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'small',
             'ul', 'h1', 'h2', 'h3', 'h4', 'h5' 'h6', 'p']


class WriteBlogForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired()])
    subtitle = StringField("副标题", validators=[DataRequired()])
    archive = StringField("归档")
    context = PageDownField("博客内容", validators=[DataRequired()])
    submit = SubmitField("提交博客")


class WriteCommentForm(FlaskForm):
    context = TextAreaField(validators=[DataRequired()])
    submit = SubmitField("评论")


@docx.route('/<int:page>')
def docx_page(page: int = 1):
    if page < 1:
        app.HBlogFlask.print_user_opt_fail_log(f"Load docx list with error page({page})")
        abort(404)
        return

    blog_list = BlogArticle.get_blog_list(limit=20, offset=(page - 1) * 20)
    max_page = app.HBlogFlask.get_max_page(BlogArticle.get_blog_count(), 20)
    page_list = app.HBlogFlask.get_page("docx.docx_page", page, max_page)
    app.HBlogFlask.print_load_page_log(f"docx list (page: {page})")
    return render_template("docx/docx.html",
                           blog_list=blog_list,
                           is_top=DBBit.BIT_1,
                           page_list=page_list,
                           form=WriteBlogForm(),
                           show_delete=current_user.check_role("DeleteBlog"))


@docx.route('/<int:archive>/<int:page>')
def archive_page(archive: int, page: int = 1):
    if page < 1:
        app.HBlogFlask.print_user_opt_fail_log(f"Load archive-docx list with error page({page}) archive: {archive}")
        abort(404)
        return

    blog_list = BlogArticle.get_blog_list(archive_id=archive, limit=20, offset=(page - 1) * 20)
    max_page = app.HBlogFlask.get_max_page(BlogArticle.get_blog_count(archive_id=archive), 20)
    page_list = app.HBlogFlask.get_page("docx.archive_page", page, max_page)
    app.HBlogFlask.print_load_page_log(f"archive-docx list (archive-id: {archive} page: {page})")
    return render_template("docx/docx.html",
                           blog_list=blog_list,
                           is_top=DBBit.BIT_1,
                           page_list=page_list,
                           form=None)


@docx.route('/article/<int:blog_id>')
def article_page(blog_id: int):
    article = load_blog_by_id(blog_id)
    if article is None:
        app.HBlogFlask.print_user_opt_fail_log(f"Load article with error id({blog_id})")
        abort(404)
        return
    app.HBlogFlask.print_load_page_log(f"article (id: {blog_id})")
    return render_template("docx/article.html",
                           article=article,
                           archive_list=article.archive,
                           form=WriteCommentForm(),
                           show_delete=current_user.check_role("DeleteComment"),
                           show_email=current_user.check_role("ReadUserInfo"))


@docx.route('/down/<int:blog_id>')
def article_down_page(blog_id: int):
    article = load_blog_by_id(blog_id)
    if article is None:
        app.HBlogFlask.print_user_opt_fail_log(f"Download article with error id({blog_id})")
        abort(404)
        return

    response = make_response(article.context)
    response.headers["Content-Disposition"] = f"attachment;filename={article.title.encode().decode('latin-1')}.html"
    app.HBlogFlask.print_load_page_log(f"download article (id: {blog_id})")
    return response


@docx.route('/comment/<int:blog>', methods=["POST"])
@login_required
def comment_page(blog: int):
    form = WriteCommentForm()
    if form.validate_on_submit():
        auth: User = current_user
        if not auth.check_role("WriteComment"):  # 检查是否具有权限
            app.HBlogFlask.print_user_not_allow_opt_log("comment")
            abort(403)
            return

        context = form.context.data
        if Comment(None, blog, auth, context).create():
            app.HBlogFlask.print_user_opt_success_log("comment")
            flash("评论成功")
        else:
            app.HBlogFlask.print_user_opt_error_log("comment")
            flash("评论失败")
        return redirect(url_for("docx.article_page", blog_id=blog))
    app.HBlogFlask.print_form_error_log("comment")
    abort(404)


@docx.route('/create-docx', methods=["POST"])
@login_required
def create_docx_page():
    form = WriteBlogForm()
    if form.validate_on_submit():
        auth: User = current_user
        if not auth.check_role("WriteBlog"):  # 检查是否具有写入权限
            app.HBlogFlask.print_user_not_allow_opt_log("write blog")
            abort(403)
            return

        title = form.title.data
        if len(title) > 10:
            flash("标题太长了")
            abort(400)

        subtitle = form.subtitle.data
        if len(subtitle) > 10:
            flash("副标题太长了")
            abort(400)

        archive = set(str(form.archive.data).replace(" ", "").split(";"))
        archive_list = []
        for f in archive:
            f_ = load_archive_by_name(f)
            if f_ is not None:
                archive_list.append(f_)

        context = bleach.linkify(
            bleach.clean(
                markdown(form.context.data, output_format='html'), tags=allow_tag, strip=True))

        if BlogArticle(None, current_user, title, subtitle, context, archive=archive_list).create():
            app.HBlogFlask.print_sys_opt_success_log("write blog")
            flash(f"博客 {title} 发表成功")
        else:
            app.HBlogFlask.print_sys_opt_fail_log("write blog")
            flash(f"博客 {title} 发表失败")
        return redirect(url_for("docx.docx_page", page=1))
    app.HBlogFlask.print_form_error_log("write blog")
    abort(404)


@docx.route("delete/<int:blog_id>")
@login_required
def delete_blog_page(blog_id: int):
    if not current_user.check_role("DeleteBlog"):
        app.HBlogFlask.print_user_not_allow_opt_log("delete blog")
        abort(403)
        return

    if BlogArticle(blog_id, None, None, None, None).delete():
        app.HBlogFlask.print_sys_opt_success_log("delete blog")
        flash("博文删除成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log("delete blog")
        flash("博文删除失败")
    return redirect(url_for("docx.docx_page", page=1))


@docx.route("delete_comment/<int:comment_id>")
@login_required
def delete_comment_page(comment_id: int):
    if not current_user.check_role("DeleteComment"):
        app.HBlogFlask.print_user_not_allow_opt_log("delete comment")
        abort(403)
        return

    if Comment(comment_id, None, None, None).delete():
        app.HBlogFlask.print_sys_opt_success_log("delete comment")
        flash("博文评论成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log("delete comment")
        flash("博文评论失败")
    return redirect(url_for("docx.docx_page", page=1))


@docx.context_processor
def inject_base():
    return {"top_nav": ["", "", "active", "", "", ""]}