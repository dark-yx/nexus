from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_session import Session
from .config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)
    Session(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
