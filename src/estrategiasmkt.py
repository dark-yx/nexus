import openai
from openai import OpenAI
import config
from utils import get_language_context, get_user_display_name, get_base_system_message

# Configurar la API de OpenAI con tu clave de API
client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

def get_system_message(db, user_id):
    # Obtener el contexto de idioma y nombre del usuario
    lang_context = get_language_context(db, user_id)
    display_name = get_user_display_name(db, user_id)

    # Construir el mensaje del sistema
    base_message = get_base_system_message(display_name, lang_context['name'])
    expert_message = "Eres un experto en estrategias de marketing digital y growth hacking."
    
    return base_message + " " + expert_message

def process_marketing_strategy(business_model, value_proposition, ideal_customer, current_revenue, commercial_goal, current_challenge, available_resources, effort_level, business_name, user_id, db):
    """Procesa una estrategia de marketing usando OpenAI."""
    try:
        prompt = f"""
        Basado en la siguiente información, genera una estrategia de marketing detallada:
        Modelo de negocio: {business_model}
        Propuesta de valor: {value_proposition}
        Cliente ideal: {ideal_customer}
        Ingresos actuales: ${current_revenue}
        Objetivo comercial: {commercial_goal}
        Desafío actual: {current_challenge}
        Recursos disponibles: {available_resources}
        Nivel de esfuerzo: {effort_level}
        Nombre del negocio: {business_name}

        Por favor, proporciona:
        1. Análisis de la situación actual
        2. Estrategia de marketing detallada
        3. Plan de implementación
        4. Métricas de seguimiento
        5. Recomendaciones específicas
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": get_system_message(db, user_id)},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al procesar la estrategia de marketing: {str(e)}"

