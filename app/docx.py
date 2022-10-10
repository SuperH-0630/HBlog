from flask import Blueprint, render_template, abort, redirect, url_for, flash, make_response, g, request
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import HiddenField, TextAreaField, StringField, SelectMultipleField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length
from typing import Optional

import app
from sql.base import DBBit
from object.blog import BlogArticle
from object.comment import Comment
from object.archive import Archive

docx = Blueprint("docx", __name__)


class EditorMD(FlaskForm):
    content = TextAreaField("博客内容", validators=[DataRequired(message="必须输入博客文章")])


class WriteBlogForm(EditorMD):
    title = StringField("标题", description="博文主标题",
                        validators=[
                            DataRequired(message="必须填写标题"),
                            Length(1, 20, message="标题长度1-20个字符")])
    subtitle = StringField("副标题", description="博文副标题",
                           validators=[Length(-1, 20, message="副标题长度20个字符以内")])
    archive = SelectMultipleField("归档", coerce=int)
    submit = SubmitField("提交博客")

    def __init__(self, default: bool = False, **kwargs):
        super().__init__(**kwargs)
        if default:
            self.content.data = "# Blog Title\n## Blog subtitle\nHello, World"
        archive = Archive.get_archive_list()
        self.archive_res = []
        self.archive_choices = [(-1, "None")]
        for i in archive:
            self.archive_res.append(i[0])
            self.archive_choices.append((i[0], f"{i[1]} ({i[3]})"))
        self.archive.choices = self.archive_choices

    def validate_archive(self, field):
        if -1 in field.data:
            if len(field.data) != 1:
                raise ValidationError("归档指定错误(none归档不能和其他归档同时被指定)")
        else:
            for i in field.data:
                if i not in self.archive_res:
                    raise ValidationError("错误的归档被指定")


class UpdateBlogForm(EditorMD):
    blog_id = HiddenField("ID", validators=[DataRequired()])
    submit = SubmitField("更新博客")

    def __init__(self, blog: Optional[BlogArticle] = None, **kwargs):
        super().__init__(**kwargs)
        if blog is not None:
            self.blog_id.data = blog.id
            self.content.data = blog.content


class UpdateBlogArchiveForm(FlaskForm):
    blog_id = HiddenField("ID", validators=[DataRequired()])
    archive = SelectMultipleField("归档", coerce=int)
    add = SubmitField("加入归档")
    sub = SubmitField("去除归档")

    def __init__(self, blog: Optional[BlogArticle] = None, **kwargs):
        super().__init__(**kwargs)
        archive = Archive.get_archive_list()
        self.archive_res = []
        self.archive_choices = []
        for i in archive:
            self.archive_res.append(i[0])
            self.archive_choices.append((i[0], f"{i[1]} ({i[3]})"))
        self.archive.choices = self.archive_choices
        if blog is not None:
            self.archive_data = []
            self.archive.data = self.archive_data
            for a in blog.archive:
                a: Archive
                self.archive_data.append(a)
            self.blog_id.data = blog.id

    def validate_archive(self, field):
        for i in field.data:
            if i not in self.archive_res:
                raise ValidationError("错误的归档被指定")


class WriteCommentForm(FlaskForm):
    content = TextAreaField("", description="评论正文",
                            validators=[DataRequired(message="请输入评论的内容"),
                                        Length(1, 100, message="请输入1-100个字的评论")])
    submit = SubmitField("评论")


def __load_docx_page(page: int, form: WriteBlogForm):
    if page < 1:
        app.HBlogFlask.print_user_opt_fail_log(f"Load docx list with error page({page})")
        abort(404)
        return

    blog_list = BlogArticle.get_blog_list(limit=20, offset=(page - 1) * 20)
    for i in blog_list:
        print(i[-1])


    max_page = app.HBlogFlask.get_max_page(BlogArticle.get_blog_count(), 20)
    page_list = app.HBlogFlask.get_page("docx.docx_page", page, max_page)
    app.HBlogFlask.print_load_page_log(f"docx list (page: {page})")
    return render_template("docx/docx.html",
                           page=page,
                           blog_list=blog_list,
                           is_top=DBBit.BIT_1,
                           page_list=page_list,
                           form=form,
                           show_delete=current_user.check_role("DeleteBlog"))


@docx.route('/')
def docx_page():
    page = int(request.args.get("page", 1))
    return __load_docx_page(page, WriteBlogForm(True))


@docx.route('/archive')
def archive_page():
    page = int(request.args.get("page", 1))
    archive = int(request.args.get("archive", 1))
    if page < 1:
        app.HBlogFlask.print_user_opt_fail_log(f"Load archive-docx list with error page({page}) archive: {archive}")
        abort(404)
        return

    blog_list = BlogArticle.get_blog_list(archive_id=archive, limit=20, offset=(page - 1) * 20)
    max_page = app.HBlogFlask.get_max_page(BlogArticle.get_blog_count(archive_id=archive), 20)
    page_list = app.HBlogFlask.get_page("docx.archive_page", page, max_page)
    app.HBlogFlask.print_load_page_log(f"archive-docx list (archive-id: {archive} page: {page})")
    return render_template("docx/docx.html",
                           page=page,
                           blog_list=blog_list,
                           is_top=DBBit.BIT_1,
                           page_list=page_list,
                           form=None)


def __load_article_page(blog_id: int, form: WriteCommentForm,
                        view: Optional[UpdateBlogForm] = None,
                        archive: Optional[UpdateBlogArchiveForm] = None):
    article = BlogArticle(blog_id)
    if article is None:
        app.HBlogFlask.print_user_opt_fail_log(f"Load article with error id({blog_id})")
        abort(404)
        return
    app.HBlogFlask.print_load_page_log(f"article (id: {blog_id})")
    if view is None:
        view = UpdateBlogForm(article)
    if archive is None:
        archive = UpdateBlogArchiveForm(article)
    print(article.top)
    return render_template("docx/article.html",
                           article=article,
                           archive_list=article.archive,
                           form=form,
                           view=view,
                           archive=archive,
                           can_update=current_user.check_role("WriteBlog"),
                           show_delete=current_user.check_role("DeleteComment"),
                           show_email=current_user.check_role("ReadUserInfo"))


@docx.route('/article')
def article_page():
    blog_id = int(request.args.get("blog", 1))
    return __load_article_page(blog_id, WriteCommentForm())


@docx.route('/article/download')
def article_down_page():
    blog_id = int(request.args.get("blog", 1))
    article = BlogArticle(blog_id)
    if article is None:
        app.HBlogFlask.print_user_opt_fail_log(f"Download article with error id({blog_id})")
        abort(404)
        return

    response = make_response(article.content)
    response.headers["Content-Disposition"] = f"attachment;filename={article.title.encode().decode('latin-1')}.md"
    app.HBlogFlask.print_load_page_log(f"download article (id: {blog_id})")
    return response


@docx.route('/article/create', methods=["POST"])
@login_required
@app.form_required(WriteBlogForm, "write blog", lambda form: __load_docx_page(int(request.args.get("page", 1)), form))
@app.role_required("WriteBlog", "write blog")
def create_docx_page():
    form: WriteBlogForm = g.form
    title = form.title.data
    subtitle = form.subtitle.data
    archive = []
    if -1 not in form.archive.data:
        for i in form.archive.data:
            i = Archive(i)
            if i is not None:
                archive.append(i)

    if BlogArticle.create(title, subtitle, form.content.data, archive, current_user):
        app.HBlogFlask.print_sys_opt_success_log("write blog")
        flash(f"博客 {title} 发表成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log("write blog")
        flash(f"博客 {title} 发表失败")
    return redirect(url_for("docx.docx_page", page=1))


@docx.route('/article/update', methods=["POST"])
@login_required
@app.form_required(UpdateBlogForm, "update blog",
                   lambda form: __load_article_page(form.id.data, WriteCommentForm(), form))
@app.role_required("WriteBlog", "write blog")
def update_docx_page():
    form: UpdateBlogForm = g.form
    if BlogArticle(form.blog_id.data).update(form.content.data):
        app.HBlogFlask.print_sys_opt_success_log("update blog")
        flash("博文更新成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log("update blog")
        flash("博文更新失败")
    return redirect(url_for("docx.article_page", blog=form.blog_id.data))


@docx.route("/article/delete")
@login_required
@app.role_required("DeleteBlog", "delete blog")
def delete_blog_page():
    blog_id = int(request.args.get("blog", -1))
    if blog_id == -1:
        return abort(400)
    if BlogArticle(blog_id).delete():
        app.HBlogFlask.print_sys_opt_success_log("delete blog")
        flash("博文删除成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log("delete blog")
        flash("博文删除失败")
    return redirect(url_for("docx.docx_page", page=1))


@docx.route("/article/set/top")
@login_required
@app.role_required("WriteBlog", "set blog top")
def set_blog_top_page():
    blog_id = int(request.args.get("blog", -1))
    top = request.args.get("top", '0') != '0'
    if blog_id == -1:
        return abort(400)
    blog = BlogArticle(blog_id)
    blog.top = top
    if top == blog.top:
        app.HBlogFlask.print_sys_opt_success_log(f"set blog top ({top})")
        flash(f"博文{'取消' if not top else ''}置顶成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log(f"set blog top ({top})")
        flash(f"博文{'取消' if not top else ''}置顶失败")
    return redirect(url_for("docx.article_page", blog=blog_id))


@docx.route("/article/set/archive", methods=["POST"])
@login_required
@app.form_required(UpdateBlogArchiveForm, "update archive",
                   lambda form: __load_article_page(form.id.data, WriteCommentForm(), UpdateBlogForm(), form))
@app.role_required("WriteBlog", "update archive")
def update_archive_page():
    form: UpdateBlogArchiveForm = g.form
    article = BlogArticle(form.blog_id.data)
    add = request.args.get("add", '0') != '0'
    for i in form.archive.data:
        if add:
            article.add_to_archive(i)
        else:
            article.sub_from_archive(i)
    flash("归档设定完成")
    return redirect(url_for("docx.article_page", blog=form.blog_id.data))


@docx.route('/comment/create', methods=["POST"])
@login_required
@app.form_required(WriteCommentForm, "write comment",
                   lambda form: __load_article_page(int(request.args.get("blog", 1)), form))
@app.role_required("WriteComment", "write comment")
def comment_page():
    blog_id = int(request.args.get("blog", 1))
    form: WriteCommentForm = g.form
    content = form.content.data
    if Comment.create(BlogArticle(blog_id), current_user, content):
        app.HBlogFlask.print_user_opt_success_log("comment")
        flash("评论成功")
    else:
        app.HBlogFlask.print_user_opt_error_log("comment")
        flash("评论失败")
    return redirect(url_for("docx.article_page", blog=blog_id))


@docx.route("/comment/delete")
@login_required
@app.role_required("DeleteComment", "delete comment")
def delete_comment_page():
    comment_id = int(request.args.get("comment", 1))
    if Comment(comment_id).delete():
        app.HBlogFlask.print_sys_opt_success_log("delete comment")
        flash("博文评论成功")
    else:
        app.HBlogFlask.print_sys_opt_fail_log("delete comment")
        flash("博文评论失败")
    return redirect(url_for("docx.docx_page", page=1))


@docx.context_processor
def inject_base():
    """ docx 默认模板变量 """
    return {"top_nav": ["", "", "active", "", "", ""]}
