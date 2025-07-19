import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import pandas as pd
import plotly.graph_objects as go
import openai
from openai import OpenAI
from utils import get_language_context

def load_prompt_from_file(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()

def initialize_facebook_api(access_token, app_secret, app_id):
    FacebookAdsApi.init(access_token=access_token, app_secret=app_secret, app_id=app_id)

def get_facebook_data(ad_account_id, start_date, end_date):
    fields = [
        'campaign_id', 'campaign_name', 'objective', 'spend', 'impressions', 
        'cpm', 'clicks', 'cpc', 'reach', 'actions', 'action_values', 
        'cost_per_action_type'
    ]
    params = {
        'level': 'campaign',
        'filtering': [],
        'time_range': {'since': start_date, 'until': end_date}
    }
    results = (AdAccount(ad_account_id).get_insights(fields=fields, params=params))

    data = []
    for result in results:
        data.append(result)
    
    while 'paging' in results and 'next' in results['paging']:
        results = results.next()
        data.extend(results)
    
    return data

def transform_campaign_data(data):
    campaigns = []

    for campaign in data:
        campaign_dict = {
            'campaign_id': campaign['campaign_id'],
            'campaign_name': campaign['campaign_name'],
            'objective': campaign['objective'],
            'clicks': campaign.get('clicks', 0),
            'cpc': campaign.get('cpc', 0),
            'impressions': campaign.get('impressions', 0),
            'cpm': campaign.get('cpm', 0),
            'reach': campaign.get('reach', 0),
            'spend': campaign.get('spend', 0),
            'leads': 0,
            'cost_per_lead': None,
            'messages': None,
            'cost_per_message': None,
            'interactions': None,
            'cost_per_interaction': None,
            'date_start': campaign.get('date_start'),
            'date_stop': campaign.get('date_stop')
        }

        for action in campaign.get('actions', []):
            action_type = action['action_type']
            action_value = int(action['value'])  # Convertir a entero

            if action_type in ['lead', 'leadgen_grouped', 'onsite_conversion.lead_grouped']:
                campaign_dict['leads'] += action_value
            elif action_type == 'onsite_conversion.messaging_conversation_started_7d':
                campaign_dict['messages'] = action_value
            elif action_type == 'post_engagement':
                campaign_dict['interactions'] = action_value

            campaign_dict[f'action_{action_type}'] = action_value

        for cpa in campaign.get('cost_per_action_type', []):
            cpa_type = cpa['action_type']
            cpa_value = cpa['value']

            if cpa_type in ['lead', 'leadgen_grouped', 'onsite_conversion.lead_grouped']:
                campaign_dict['cost_per_lead'] = cpa_value
            elif cpa_type == 'onsite_conversion.messaging_conversation_started_7d':
                campaign_dict['cost_per_message'] = cpa_value
            elif cpa_type == 'post_engagement':
                campaign_dict['cost_per_interaction'] = cpa_value

            campaign_dict[f'cost_per_{cpa_type}'] = cpa_value

        campaigns.append(campaign_dict)

    df = pd.DataFrame(campaigns)
    desired_columns = [
        'campaign_id', 'campaign_name', 'objective', 'clicks', 'cpc', 
        'impressions', 'cpm', 'reach', 'spend', 'leads', 'cost_per_lead', 
        'messages', 'cost_per_message', 'interactions', 'cost_per_interaction',
        'date_start', 'date_stop'
    ]
    df = df[desired_columns]

    return df

def create_pie_chart(df, column):
    fig = go.Figure(data=[go.Pie(
        labels=df['campaign_name'], 
        values=df[column], 
        hole=.3,
        textinfo='percent+label',  # Muestra porcentaje y etiquetas
        insidetextorientation='radial',
        textfont=dict(color='white'),  # Cambia el color del texto a blanco
        marker=dict(line=dict(color='white', width=2))  # Bordes en blanco para mayor contraste
    )])
    
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-1.5,  # Ajustar el valor según sea necesario para colocar la leyenda más abajo
            xanchor="center",
            x=0.5,
            font=dict(color='white')  # Cambia el color de la leyenda a blanco
        ),
        margin=dict(l=0, r=0, t=50, b=300),  # Aumentar el margen inferior para agregar espacio
        paper_bgcolor='rgba(0,0,0,0)',  # Fondo transparente
        plot_bgcolor='rgba(0,0,0,0)',  # Fondo del gráfico transparente
    )
    
    return fig.to_html(full_html=False)


def generate_campaign_summary(campaign_data, prompt, db=None, user_id=None):
    campaign_summaries = []
    for _, row in campaign_data.iterrows():
        campaign_summary = f"""
        Campaña: {row['campaign_name']}
        Objetivo: {row['objective']}
        Clicks: {row['clicks']}
        CPC: {row['cpc']}
        Impresiones: {row['impressions']}
        CPM: {row['cpm']}
        Alcance: {row['reach']}
        Gasto: {row['spend']}
        Leads: {row['leads']}
        Costo por Lead: {row['cost_per_lead']}
        Mensajes: {row['messages']}
        Costo por Mensaje: {row['cost_per_message']}
        Interacciones: {row['interactions']}
        Costo por Interacción: {row['cost_per_interaction']}
        Fecha Inicio: {row['date_start']}
        Fecha Fin: {row['date_stop']}
        """
        campaign_summaries.append(campaign_summary.strip())

    full_campaign_summary = "\n\n".join(campaign_summaries)
    
    # Obtener el contexto de idioma
    lang_context = get_language_context(db, user_id)
    
    messages = [
        {"role": "system", "content": f"Eres un experto en análisis de campañas publicitarias de Facebook. Responde en {lang_context['name']}."},
        {"role": "user", "content": f"Datos de campaña:\n{full_campaign_summary}\n\n{prompt}\n\nIMPORTANTE: Responde en {lang_context['name']}."}
    ]
    
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f'Error al generar el resumen: {str(e)}'
    return answer

def generate_analysis(access_token, ad_account_id, start_date, end_date, prompt_file, db=None, user_id=None):
    initialize_facebook_api(access_token)
    raw_data = get_facebook_data(ad_account_id, start_date, end_date)
    campaign_data = transform_campaign_data(raw_data)
    prompt = load_prompt_from_file(os.path.join("prompts", prompt_file))
    pie_charts = {col: create_pie_chart(campaign_data, col) for col in ['spend', 'clicks', 'impressions', 'leads', 'messages']}
    
    # Obtener el contexto de idioma
    lang_context = get_language_context(db, user_id)
    
    messages = [
        {"role": "system", "content": f"Eres un experto en análisis de campañas publicitarias de Facebook. Responde en {lang_context['name']}."},
        {"role": "user", "content": f"{prompt}\n\nIMPORTANTE: Responde en {lang_context['name']}."}
    ]
    
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        campaign_summary = response.choices[0].message.content
    except Exception as e:
        campaign_summary = f"Error al generar el resumen: {str(e)}"
        
    return campaign_data, pie_charts['spend'], pie_charts['clicks'], pie_charts['impressions'], pie_charts['leads'], pie_charts['messages'], campaign_summary
