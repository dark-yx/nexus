from datetime import datetime
import openai
from db import check_user_credits, update_user_credits

def get_token_usage(response):
    return response['usage']['total_tokens']

def use_tokens(db, user_id, messages, tool_name, credit_cost):
    cursor = db.connection.cursor()
    cursor.execute("SELECT tokens, credits FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        return {'error': 'User not found'}

    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
    tokens_used = get_token_usage(response)

    if user[0] < tokens_used:
        return {'error': 'Insufficient tokens'}

    has_credits, message = check_user_credits(db, user_id, credit_cost)
    if not has_credits:
        return {'error': message}

    new_token_balance = user[0] - tokens_used
    new_credit_balance = user[1] - credit_cost
    cursor.execute("UPDATE users SET tokens = %s, credits = %s WHERE user_id = %s", (new_token_balance, new_credit_balance, user_id))

    cursor.execute(
        "INSERT INTO token_transactions (user_id, tokens_used, tool_name, timestamp) VALUES (%s, %s, %s, %s)",
        (user_id, tokens_used, tool_name, datetime.utcnow())
    )

    db.connection.commit()
    cursor.close()

    return {'message': 'Tool used successfully', 'tokens_used': tokens_used, 'remaining_tokens': new_token_balance, 'remaining_credits': new_credit_balance, 'response': response}

def call_openai_api(db, user_id, messages, tool_name, credit_cost):
    result = use_tokens(db, user_id, messages, tool_name, credit_cost)
    if 'error' in result:
        return {'error': result['error']}
    response = result['response']
    try:
        answer = response['choices'][0]['message']['content']
    except:
        answer = 'Oops, venciste a la IA, prueba con una pregunta diferente. Si el problema persiste, vuelve a intentarlo más tarde.'
    return {'answer': answer}

def get_token_usage_summary(db):
    cursor = db.connection.cursor()
    cursor.execute(
        "SELECT tool_name, SUM(tokens_used) as total_tokens FROM token_transactions GROUP BY tool_name"
    )
    summary = cursor.fetchall()
    cursor.close()
    return summary

def get_user_token_usage(db, user_id):
    cursor = db.connection.cursor()
    cursor.execute(
        "SELECT tool_name, tokens_used, timestamp FROM token_transactions WHERE user_id = %s", (user_id,)
    )
    usage = cursor.fetchall()
    cursor.close()
    return usage

def get_average_token_usage_per_user(db):
    cursor = db.connection.cursor()
    cursor.execute(
        "SELECT tool_name, AVG(tokens_used) as avg_tokens FROM token_transactions GROUP BY tool_name"
    )
    avg_usage = cursor.fetchall()
    cursor.close()
    return avg_usage

def get_total_and_average_token_usage_per_user(db):
    cursor = db.connection.cursor()
    cursor.execute(
        "SELECT user_id, tool_name, SUM(tokens_used) as total_tokens, AVG(tokens_used) as avg_tokens FROM token_transactions GROUP BY user_id, tool_name"
    )
    usage = cursor.fetchall()
    cursor.close()
    return usage