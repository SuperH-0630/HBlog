from view import WebApp
from waitress import serve


web = WebApp(__name__)
app = web.get_app()


if __name__ == '__main__':
    print("已启动服务: 127.0.0.1:8080")
    serve(app, host='0.0.0.0', port="8080")
