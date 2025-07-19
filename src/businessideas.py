import openai
from openai import OpenAI
import config
from db import check_user_credits
from utils import get_language_context, get_user_display_name, get_base_system_message

# Configurar la API de OpenAI con tu clave de API
client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

def get_system_message(db, user_id):
    # Obtener el contexto de idioma y nombre del usuario
    lang_context = get_language_context(db, user_id)
    display_name = get_user_display_name(db, user_id)

    # Construir el mensaje del sistema
    base_message = get_base_system_message(display_name, lang_context['name'])
    expert_message = "Eres un experto en emprendimiento y desarrollo de negocios."
    
    return base_message + " " + expert_message

def process_business_idea(skills, interests, capital, economic_scenario, dedication, user_id, db):
    """Procesa una idea de negocio usando OpenAI."""
    try:
        # Verificar créditos
        has_credits, message = check_user_credits(db, user_id, 2)
        if not has_credits:
            return message

        prompt = f"""
        Basado en la siguiente información, genera una idea de negocio detallada:
        Habilidades: {skills}
        Intereses: {interests}
        Capital disponible: ${capital}
        Escenario económico: {economic_scenario}
        Nivel de dedicación: {dedication}

        Por favor, proporciona:
        1. Descripción detallada del negocio
        2. Análisis de viabilidad
        3. Plan de implementación
        4. Estrategia de marketing
        5. Proyecciones financieras
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
        return f"Error al procesar la idea de negocio: {str(e)}"
