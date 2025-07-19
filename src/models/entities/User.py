from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, name='user_id')
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255))
    approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    first_login = db.Column(db.Boolean, default=True)
    credits = db.Column(db.Float, default=10.0)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    phone = db.Column(db.String(255))
    meta_access_token = db.Column(db.String(255))
    app_secret = db.Column(db.String(255))
    app_id = db.Column(db.String(255))
    ad_account_id = db.Column(db.String(255))
    sector = db.Column(db.String(255))
    how_did_you_hear = db.Column(db.String(255))
    reason_to_try = db.Column(db.String(255))
    user_type = db.Column(db.String(255))
    preferred_language = db.Column(db.String(10))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)