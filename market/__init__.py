from flask import Flask
import flask_login
from flask_bcrypt import Bcrypt, bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from sqlalchemy import true #for login


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///market.db'
db=SQLAlchemy(app)
app.config['SECRET_KEY']='405ccfeb09e3f35cdc0e3f1a'

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login_page"

from market import routes
