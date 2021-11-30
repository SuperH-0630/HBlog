from flask import render_template
from flask_mail import Mail, Message
from configure import conf


def send_msg(title: str, mail: Mail, to, template, **kwargs):
    message = Message(conf['email_prefix'] + title, sender=f"HBlog Admin <{conf['email_sender']}>", recipients=[to])
    message.body = render_template("email-msg/" + f"{template}.txt", **kwargs)
    mail.send(message)
