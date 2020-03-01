from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
#from flask_login import LoginManager

app = Flask(__name__)

from store import routes
