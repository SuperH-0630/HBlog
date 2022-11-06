# HBlog
## 介绍
`HBlog`是基于Python和Flask的博客系统。

* 具有博文、博文评论、博文归档的功能。
* 具有博客留言的功能。
* 访客注册、角色管理的功能。
* 文件存储的功能。
* 具有管理员管理后台。

## 部署
### 下载
```shell
$ useradd hblog -m
$ git clone https://github.com/SuperH-0630/HBlog.git /home/hblog/.HBlog
```

### 下载依赖
```shell
$ sudo -u hblog python3.10 -m pip install -r /home/hblog/.HBlog/requirements.txt --user
$ sudo -u hblog python3.10 -m pip install gunicorn gevent --user
```

### 配置
创建配置文件`etc/hblog/conf.json`，配置文件内容如下：
```json
{
  "DEBUG_PROFILE": false,
  "SECRET_KEY": "随机密钥",

  "BLOG_NAME": "",
  "BLOG_DESCRIBE": "",
  "INTRODUCE": {
    "介绍的名称": "可任意创建更多介绍"
  },
  "INTRODUCE_LINK": {
    "连接名称": "可任意创建更多连接"
  },
  "ABOUT_ME_PAGE": "about_me.html静态页面的地址",
  "FOOT": "页脚信息",

  "MYSQL_URL": "",
  "MYSQL_PORT": 3306,
  "MYSQL_NAME": "",
  "MYSQL_PASSWD": "",
  "MYSQL_DATABASE": "",

  "REDIS_HOST": "",
  "REDIS_PORT": 6379,
  "REDIS_NAME": "",
  "REDIS_PASSWD": "",
  "REDIS_DATABASE": 0,

  "CACHE_REDIS_HOST": "",
  "CACHE_REDIS_PORT": 6379,
  "CACHE_REDIS_NAME": "",
  "CACHE_REDIS_PASSWD": "",
  "CACHE_REDIS_DATABASE": 0,

  "MAIL_SERVER": "SMTP服务地址",
  "MAIL_PORT": 465,
  "MAIL_USE_TLS": false,
  "MAIL_USE_SSL": true,
  "MAIL_USERNAME": "",
  "MAIL_PASSWORD": "@0630",
  "MAIL_SENDER": "名字 <发件人地址>",

  "USE_ALIYUN": true,
  "ALIYUN_KEY": "阿里云OOS的账号Key",
  "ALIYUN_SECRET": "",
  "ALIYUN_BUCKET_ENDPOINT": "",
  "ALIYUN_BUCKET_IS_CNAME": false,
  "ALIYUN_BUCKET_NAME": "",
  "ALIYUN_BUCKET_USE_SIGN_URL": false,

  "LOG_LEVEL": "debug",
  "LOG_HOME": "log",
  "LOG_SENDER": true,

  "LOGO": "Logo的文件名，存储在static目录的相对路径",
  "ICP": {
    "备案的域名": "ICP备案"
  },
  "GONG_AN": {
    "备案的域名": "公安备案"
  }
}
```

### 静态`AboutMe.html`页面
一个普通的HTML页面，必须包含`<div class="about-me"> </div>`，这部分内容会被显示在博客上。

### 创建`systemd`服务文件
```serivce
[Unit]
Description=HBlog server on 8080
After=network.target auditd.service

[Service]
User=hblog
Group=hblog
WorkingDirectory=/home/hblog/.HBlog/
ExecStart=python3.10的路径 -m gunicorn -c /home/hblog/.HBlog/gunicorn.conf.py main:app --preload -b 0.0.0.0:8080
Type=simple
Environment="HBLOG_CONF=/etc/hblog/conf.json"
 
[Install]
WantedBy=multi-user.targe
```

## 样例博客
我的博客就是用HBlog搭建的，访问：[是桓的小窝](https://www.song-zh.com)。
