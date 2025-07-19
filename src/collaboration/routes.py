
from flask import Blueprint, request, jsonify
from .. import db
from .models import Workspace, Channel, Message

collaboration = Blueprint('collaboration', __name__)

@collaboration.route('/workspaces', methods=['POST'])
def create_workspace():
    data = request.get_json()
    new_workspace = Workspace(name=data['name'])
    db.session.add(new_workspace)
    db.session.commit()
    return jsonify({'message': 'Workspace created'})

@collaboration.route('/workspaces/<int:workspace_id>/channels', methods=['POST'])
def create_channel(workspace_id):
    data = request.get_json()
    new_channel = Channel(name=data['name'], workspace_id=workspace_id)
    db.session.add(new_channel)
    db.session.commit()
    return jsonify({'message': 'Channel created'})

@collaboration.route('/channels/<int:channel_id>/messages', methods=['POST'])
def post_message(channel_id):
    data = request.get_json()
    new_message = Message(content=data['content'], user_id=data['user_id'], channel_id=channel_id)
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'message': 'Message posted'})
