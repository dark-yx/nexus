import openai
from openai import OpenAI
import config
from db import check_user_credits, get_user_preferred_language
import json
from utils import get_language_context, get_user_display_name, get_base_system_message

# Configurar la API de OpenAI con tu clave de API
client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

def get_system_message(db, user_id, tipo_analisis):
    # Obtener el contexto de idioma y nombre del usuario
    lang_context = get_language_context(db, user_id)
    display_name = get_user_display_name(db, user_id)

    # Mensajes base según el tipo de análisis
    base_messages = {
        'engagement': "Como experto en Estrategias de Marketing Digital, proporciona observaciones de la tasa de engagement obtenida en nuestra calculadora. Da recomendaciones y observaciones sobre cómo mejorar la interacción con la audiencia en las redes sociales de la empresa. No proporciones explicacion de como calcular ni las formulas, solo centrate en la importancia de la interacción con la audiencia y las estrategias de redes sociales para mejorarla.",
        'conversion': "Como experto en Estrategias de Marketing Digital, CRO y Growth Hacking, proporciona observaciones de la tasa de conversión obtenida en nuestra calculadora. Da recomendaciones y observaciones sobre cómo potenciar las conversiones. No proporciones explicacion de como calcular ni las formulas, solo centrate en la importancia del CRO y las estrategias para mejorarlo.",
        'roi': "Como experto en Estrategias de Marketing Digital, CRO y Growth Hacking, proporciona observaciones del ROI obtenido en nuestra calculadora. Da recomendaciones y observaciones sobre cómo maximizar el ROI (Retorno a la Inversión). No proporciones explicacion de como calcular ni las formulas, solo centrate en la importancia de optimizar el ROI y las estrategias para mejorarlo."
    }

    # Construir el mensaje del sistema
    return get_base_system_message(display_name, lang_context['name']) + " " + base_messages[tipo_analisis]

def generar_resumen_engagement(prompt, user_id, db):
    # Verificar créditos
    has_credits, message = check_user_credits(db, user_id, 1)
    if not has_credits:
        return message

    messages = [
        {"role": "system", "content": get_system_message(db, user_id, 'engagement')},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    try:
        answer = response.choices[0].message.content
    except:
        answer = 'Oops, venciste a la IA, prueba con una pregunta diferente. Si el problema persiste, vuelve a intentarlo más tarde.'

    return answer

def generar_resumen_conversion(prompt, user_id, db):
    # Verificar créditos
    has_credits, message = check_user_credits(db, user_id, 1)
    if not has_credits:
        return message

    messages = [
        {"role": "system", "content": get_system_message(db, user_id, 'conversion')},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    try:
        answer = response.choices[0].message.content
    except:
        answer = 'Oops, venciste a la IA, prueba con una pregunta diferente. Si el problema persiste, vuelve a intentarlo más tarde.'

    return answer

def generar_resumen_roi(prompt, user_id, db):
    # Verificar créditos
    has_credits, message = check_user_credits(db, user_id, 1)
    if not has_credits:
        return message

    messages = [
        {"role": "system", "content": get_system_message(db, user_id, 'roi')},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    try:
        answer = response.choices[0].message.content
    except:
        answer = 'Oops, venciste a la IA, prueba con una pregunta diferente. Si el problema persiste, vuelve a intentarlo más tarde.'

    return answer

def calcular_datos(data, user_id, db):
    conversion_rate = None
    summary_content_conversion = None
    roi = None
    summary_content_roi = None
    engagement_rate = None
    summary_content_engagement = None

    if data.get('type') == 'conversion':
        visitors = float(data.get('visitors', 0))
        conversions = float(data.get('conversions', 0))
        conversion_rate = round((conversions / visitors) * 100, 2)
        data = {
            'visitors': visitors,
            'conversions': conversions,
            'conversion_rate': conversion_rate
        }
        prompt = f"""
        Analiza los siguientes datos de conversión:
        {json.dumps(data, indent=2)}

        Por favor, proporciona un análisis detallado incluyendo:
        1. Interpretación de los resultados
        2. Puntos fuertes y débiles
        3. Recomendaciones para mejorar
        4. Conclusiones y próximos pasos
        """
        summary_content_conversion = generar_resumen_conversion(prompt, user_id, db)
    
    elif data.get('type') == 'roi':
        ganancias = float(data.get('ganancias', 0))
        costos = float(data.get('costos', 0))
        roi = round(((ganancias - costos) / costos) * 100, 2)
        data = {
            'ganancias': ganancias,
            'costos': costos,
            'roi': roi
        }
        prompt = f"""
        Analiza los siguientes datos de ROI:
        {json.dumps(data, indent=2)}

        Por favor, proporciona un análisis detallado incluyendo:
        1. Interpretación de los resultados
        2. Puntos fuertes y débiles
        3. Recomendaciones para mejorar
        4. Conclusiones y próximos pasos
        """
        summary_content_roi = generar_resumen_roi(prompt, user_id, db)
    
    elif data.get('type') == 'engagement':
        interacciones = float(data.get('interacciones', 0))
        alcance = float(data.get('alcance', 0))
        engagement_rate = round((interacciones / alcance) * 100, 2)
        data = {
            'interacciones': interacciones,
            'alcance': alcance,
            'engagement_rate': engagement_rate
        }
        prompt = f"""
        Analiza los siguientes datos de engagement:
        {json.dumps(data, indent=2)}

        Por favor, proporciona un análisis detallado incluyendo:
        1. Interpretación de los resultados
        2. Puntos fuertes y débiles
        3. Recomendaciones para mejorar
        4. Conclusiones y próximos pasos
        """
        summary_content_engagement = generar_resumen_engagement(prompt, user_id, db)

    return {
        'conversion_rate': conversion_rate,
        'summary_content_conversion': summary_content_conversion,
        'roi': roi,
        'summary_content_roi': summary_content_roi,
        'engagement_rate': engagement_rate,
        'summary_content_engagement': summary_content_engagement
    }