
import plotly.graph_objects as go
from openai import OpenAI
import config
from db import get_user_preferred_language
import traceback # Import traceback para logs de error más detallados

openai_client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)


def get_system_message(db, user_id):
    # Obtener el idioma preferido del usuario
    preferred_language = get_user_preferred_language(db, user_id)
    if not preferred_language:
        preferred_language = 'en'  # Default to English

    # Mapear el código de idioma a un nombre legible
    language_names = {
        "en": "English",
        "es": "Spanish",
        "pt": "Portuguese",
        "fr": "French"
    }
    lang_name = language_names.get(preferred_language, "English")

    # Obtener el nombre del usuario
    try:
        cursor = db.connection.cursor()
        cursor.execute("SELECT display_name FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            display_name = result[0]
        else:
            display_name = "User"
    except Exception as e:
        display_name = "User"

    # Construir el mensaje del sistema con el idioma y nombre del usuario
    system_message = (
        "Como experto en Estrategias de Marketing Digital, CRO y Growth Hacking, proporciona observaciones de la tasa de conversión obtenida en nuestra calculadora. Da recomendaciones y observaciones sobre cómo potenciar las conversiones. Genera un analisis, observaciones y recomendaciones para el embudo de conversión basado en los datos proporcionados. Debe ser detallado y estrategico, y debes cerrar el analisis con una concluison que contemple cada etapa del funnel y proporcione la mayor claridad posible del flujo del canal digital ya que el usuario no tiene la opcion de realizar preguntas adicionales."
    ).format(display_name, lang_name, lang_name)

    return system_message

def generar_embudo_grafico(embudo_data):
    print(f"[DEBUG funnel.py] Iniciando generar_embudo_grafico con embudo_data: {embudo_data}")
    try:
        labels = list(embudo_data.keys())
        data_values = list(embudo_data.values())

        chart_data_output = {
            'labels': labels,
            'data': data_values
        }
        print(f"[DEBUG funnel.py] Datos para Chart.js generados en generar_embudo_grafico: {chart_data_output}")
        return chart_data_output
    except Exception as e:
        print(f"[ERROR funnel.py] Error en generar_embudo_grafico: {str(e)}")
        print(f"[ERROR funnel.py] Traceback: {traceback.format_exc()}")
        # En caso de error, devuelve una estructura vacía o con error para Chart.js
        return {'labels': [], 'data': [], 'error': 'Error al generar datos del gráfico'}

def generar_resumen_embudo(embudo_data, user_id, db):
    print(f"[DEBUG funnel.py] Iniciando generar_resumen_embudo con embudo_data: {embudo_data}, user_id: {user_id}")
    try:
        system_msg_content = get_system_message(db, user_id)
        print(f"[DEBUG funnel.py] System Message para OpenAI: {system_msg_content[:200]}...") # Loguear solo una parte por brevedad
        
        user_msg_content = f"Estos son los datos del embudo de la empresa:{embudo_data}"
        print(f"[DEBUG funnel.py] User Message para OpenAI: {user_msg_content}")

        messages = [
            {"role": "system", "content": system_msg_content},
            {"role": "user", "content": user_msg_content}
        ]
        
        print("[DEBUG funnel.py] Enviando solicitud a OpenAI API...")
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        print(f"[DEBUG funnel.py] Respuesta de OpenAI recibida.")

        if response and response.choices and response.choices[0].message:
            resumen = response.choices[0].message.content
            print(f"[DEBUG funnel.py] Resumen extraído de OpenAI: {resumen[:200]}...") # Loguear solo una parte
        else:
            print("[ERROR funnel.py] Estructura de respuesta de OpenAI inesperada o vacía.")
            resumen = 'Error: No se pudo obtener una respuesta válida de la IA.'
            
    except Exception as e:
        print(f"[ERROR funnel.py] Error en la llamada a OpenAI o al procesar su respuesta: {str(e)}")
        print(f"[ERROR funnel.py] Traceback: {traceback.format_exc()}")
        resumen = 'Oops, venciste a la IA, prueba con una pregunta diferente. Si el problema persiste, vuelve a intentarlo más tarde. Detalle: ' + str(e)
        
    return resumen
