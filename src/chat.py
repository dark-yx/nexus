from flask import Blueprint, request, jsonify
from src.agents.langchain_chat_agent import LangchainChatAgent
from db import check_user_credits

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat_route():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        user_id = data.get('user_id')

        if not prompt or not user_id:
            return jsonify({'error': 'Missing required parameters'}), 400

        # Check if the user has sufficient credits
        has_credits, message = check_user_credits(request.app.config['mysql'], user_id, 0.1)
        if not has_credits:
            return jsonify({'error': message}), 402 # Payment Required

        # Initialize and run the Langchain agent
        agent = LangchainChatAgent(db=request.app.config['mysql'], user_id=user_id)
        response = agent.run(prompt)
        
        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500