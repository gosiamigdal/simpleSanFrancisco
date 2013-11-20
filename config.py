import os

# Config file, put all your keys and passwords and whatnot in here
DB_URI = os.environ.get("DATABASE_URL", "sqlite:///simplesf_app.db")
SECRET_KEY = "this should be a secret"
PORT = int(os.environ.get('PORT',5000))