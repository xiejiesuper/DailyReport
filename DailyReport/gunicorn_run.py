from werkzeug.contrib.fixers import ProxyFix
from DailyReport import create_app

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == "__main__":
    app.run()
