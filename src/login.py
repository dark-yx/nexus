# Importar bibliotecas necesarias
import matplotlib
matplotlib.use('Agg')  # Configurar Matplotlib para entornos no interactivos

from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import openai
from dotenv import load_dotenv
import os
import config
import requests
from bs4 import BeautifulSoup
import urllib
import json
import string
from string import ascii_lowercase
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from authlib.integrations.flask_client import OAuth
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect,  validate_csrf
from flask_login import LoginManager, login_user, logout_user, login_required
import secrets

from models.ModelUser import ModelUser
from models.entities.User import User

app = Flask(__name__)

# Cargar variables de entorno
load_dotenv()

appConfig = {
    "OAUTH2_CLIENT_ID": os.getenv("GOOGLE_OAUTH_CLIENT_ID", "tu_google_oauth_client_id_aqui"),
    "OAUTH2_CLIENT_SECRET": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "tu_google_oauth_client_secret_aqui"),
    "OAUTH2_META_URL": "https://accounts.google.com/.well-know/openid-configuration",
    "FLASK_SECRET": os.getenv("FLASK_SECRET_KEY", "tu_flask_secret_key_aqui"),
    "FLASK_PORT": int(os.getenv("FLASK_PORT", 5000))
}

oauth = OAuth(app)

oauth.register("onePum",
               client_id=appConfig.get("OAUTH2_CLIENT_ID"),
               client_secret=appConfig.get("OAUTH2_CLIENT_SECRET"),
               server_metadata_url=appConfig.get("OAUTH2_META_URL"),
               client_kwargs={
                   "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read",
               }
               )


app.secret_key = secrets.token_hex(16)  # Genera una clave secreta hexadecimal de 16 bytes
csrf = CSRFProtect()
db = MySQL(app)
login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id) 