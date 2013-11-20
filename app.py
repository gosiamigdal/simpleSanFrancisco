from flask import Flask
import config 
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

from flask.ext import login

app = Flask(__name__)
app.config.from_object(config)
admin = Admin(app)

class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()
