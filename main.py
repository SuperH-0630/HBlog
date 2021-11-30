from view import WebApp


web = WebApp(__name__)
app = web.get_app()


if __name__ == '__main__':
    app.run()
