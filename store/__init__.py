from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from store import config as c
from flask_login import LoginManager
from flask_admin import Admin


app = Flask(__name__)
app.config['SECRET_KEY'] = c.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = c.db_uri
app.config['SQLALCHEMY_POOL_RECYCLE'] = 90


@app.context_processor
def inject_globals():
    return dict(store_name=c.store_name)


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

admin = Admin(app, name='ToBeNamedAdmin', template_mode='bootstrap3')

from store import routes
from store import views