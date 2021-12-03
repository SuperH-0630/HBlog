from configure import configure
import os


env_dict = os.environ
hblog_conf = env_dict.get("hblog_conf")
if hblog_conf is None:
    print("执行配置文件: ./etc/conf.json")
    configure("./etc/conf.json")
else:
    print(f"执行配置文件: {hblog_conf}")
    configure(hblog_conf)


from view import WebApp
from waitress import serve


web = WebApp(__name__)
app = web.get_app()


if __name__ == '__main__':
    print("已启动服务: 127.0.0.1:8080")
    serve(app, host='0.0.0.0', port="8080")
