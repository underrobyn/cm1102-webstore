from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from store import config as c
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = c.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = c.db_uri

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

from store import routes
