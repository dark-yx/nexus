
from .. import db

class Workspace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', secondary='workspace_users', backref=db.backref('workspaces', lazy='dynamic'))

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    messages = db.relationship('Message', backref='channel', lazy='dynamic')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)

workspace_users = db.Table('workspace_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('workspace_id', db.Integer, db.ForeignKey('workspace.id'), primary_key=True)
)
