import os

# Config file, put all your keys and passwords and whatnot in here
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///simplesf_app.db")
SECRET_KEY = "this should be a secret"
PORT = int(os.environ.get('PORT',5000))
FB_APP_ID = os.environ.get("FB_APP_ID")
FB_DOMAIN = os.environ.get("FB_DOMAIN", "localhost:5000")
FB_SECRET = os.environ.get("FB_SECRET")
FORECAST_SECRET = os.environ.get("FORECAST_SECRET")