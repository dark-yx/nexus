import plotly.graph_objects as go
from openai import OpenAI
import config
from ..db import get_user_preferred_language

class FunnelAgent:
    def __init__(self):
        self.openai_client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

    def get_system_message(self, user_id):
        preferred_language = get_user_preferred_language(user_id)
        if not preferred_language:
            preferred_language = 'en'

        language_names = {
            "en": "English",
            "es": "Spanish",
            "pt": "Portuguese",
            "fr": "French"
        }
        lang_name = language_names.get(preferred_language, "English")

        # Esta parte necesita ser refactorizada para no depender de la BD directamente
        display_name = "User"

        system_message = (
            "Como experto en Estrategias de Marketing Digital, CRO y Growth Hacking, proporciona observaciones de la tasa de conversión obtenida en nuestra calculadora. Da recomendaciones y observaciones sobre cómo potenciar las conversiones. Genera un analisis, observaciones y recomendaciones para el embudo de conversión basado en los datos proporcionados. Debe ser detallado y estrategico, y debes cerrar el analisis con una concluison que contemple cada etapa del funnel y proporcione la mayor claridad posible del flujo del canal digital ya que el usuario no tiene la opcion de realizar preguntas adicionales."
        ).format(display_name, lang_name, lang_name)

        return system_message

    def analizar_embudo(self, data, user_id):
        embudo_data = {
            'Clics': int(data.get('clics', 0)),
            'Contactos': int(data.get('contactos', 0)),
            'Leads': int(data.get('leads_validos', 0)),
            'SQL': int(data.get('sql', 0)),
            'Negocios': int(data.get('lead_con_negocios', 0)),
            'Clientes': int(data.get('clientes', 0))
        }

        chart_data = self.generar_embudo_grafico(embudo_data)
        resumen = self.generar_resumen_embudo(embudo_data, user_id)

        return chart_data, resumen

    def generar_embudo_grafico(self, embudo_data):
        labels = list(embudo_data.keys())
        data_values = list(embudo_data.values())

        chart_data_output = {
            'labels': labels,
            'data': data_values
        }
        return chart_data_output

    def generar_resumen_embudo(self, embudo_data, user_id):
        system_msg_content = self.get_system_message(user_id)
        user_msg_content = f"Estos son los datos del embudo de la empresa:{embudo_data}"

        messages = [
            {"role": "system", "content": system_msg_content},
            {"role": "user", "content": user_msg_content}
        ]
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        if response and response.choices and response.choices[0].message:
            resumen = response.choices[0].message.content
        else:
            resumen = 'Error: No se pudo obtener una respuesta válida de la IA.'
            
        return resumen
