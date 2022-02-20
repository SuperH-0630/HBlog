from flask import render_template, current_app
from flask_mail import Mail, Message
from configure import conf
import os


def send_msg(title: str, mail: Mail, to, template, **kwargs):
    """ 邮件发送 """
    sender = f"HBlog Admin <{conf['email_sender']}>"
    template_path = os.path.join("email-msg", f"{template}.txt")
    message = Message(conf['email_prefix'] + title, sender=sender, recipients=[to])
    message.body = render_template(template_path, **kwargs)
    mail.send(message)
    current_app.logger.info(f"Send email to {to} sender: {sender} msg: {template_path} kwargs: {kwargs}")
