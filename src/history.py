from flask import Blueprint, request, jsonify, session, render_template
from db import init_db, get_user_history

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/history', methods=['GET'])
def history():
    """Endpoint para obtener el historial del usuario autenticado."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401
    
    connection = init_db()
    history_data = get_user_history(connection, user_id)

    return jsonify(history_data)

def get_analysis_by_id(connection, user_id, analysis_id):
    """Obtiene un análisis específico por su ID y usuario."""
    cursor = connection.cursor()
    
    tables = {
        "web_analysis": "analysis_summary",
        "calculator_results": "summary_content",
        "business_ideas": "business_idea",
        "marketing_strategies": "marketing_strategy",
        "funnel_analysis": "resumen",
        "facebook_ads": "summary",
        "ga4_analysis": "summary",
        "searchconsole_analysis": "summary",
    }

    for table, column in tables.items():
        query = f"SELECT {column} FROM {table} WHERE user_id = %s AND id = %s"
        cursor.execute(query, (user_id, analysis_id))
        result = cursor.fetchone()
        if result:
            cursor.close()
            return result[column]
    
    cursor.close()
    return None

@history_bp.route('/api/history/<int:analysis_id>', methods=['GET'])
def get_analysis_details(analysis_id):
    """Obtiene un análisis específico por su ID."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401
    
    connection = init_db()
    summary = get_analysis_by_id(connection, user_id, analysis_id)

    if summary:
        return jsonify({"summary": summary})
    else:
        return jsonify({"error": "Análisis no encontrado"}), 404

@history_bp.route('/history', methods=['GET'])
def history_page():
    """Renderiza la página del historial del usuario."""
    return render_template('history.html')
