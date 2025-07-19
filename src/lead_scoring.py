import pandas as pd
import os
from default_api import google_web_search

class DataProcessorAgent:
    def load_data(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        try:
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                return None, "Unsupported file type"
            return df, None
        except Exception as e:
            return None, str(e)

    def clean_and_normalize_data(self, df):
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].str.lower()
        return df

    def identify_entities(self, df):
        entity_mapping = {
            'name': ['nombre', 'name', 'full name', 'nombre completo'],
            'company': ['empresa', 'company', 'organization', 'organización'],
            'email': ['email', 'correo electrónico', 'mail']
        }
        
        identified_entities = {}
        for entity, possible_names in entity_mapping.items():
            for col in df.columns:
                if col.lower() in possible_names:
                    identified_entities[entity] = col
                    break
        return identified_entities

import requests

class DataEnrichmentAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_company_domain(self, company_name):
        try:
            search_results = google_web_search(query=f"{company_name} website")
            # Simplistic domain extraction, can be improved with more robust logic
            if search_results and search_results['results']:
                first_url = search_results['results'][0]['link']
                domain = first_url.split('//')[1].split('/')[0]
                return domain, None
            return None, "Could not find company website"
        except Exception as e:
            return None, str(e)

    def enrich_company_data(self, company_domain):
        if not self.api_key:
            return None, "Clearbit API key not configured"

        try:
            response = requests.get(
                f"https://company.clearbit.com/v2/companies/find?domain={company_domain}",
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            return None, str(e)

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

import plotly.express as px

class VisualizationAgent:
    def generate_score_distribution_chart(self, results):
        scores = [result['score'] for result in results]
        fig = px.histogram(scores, nbins=20, title='Distribución de Puntuaciones de Leads')
        return fig.to_html(full_html=False)

class PersonalizationAgent:
    def __init__(self, openai_api_key):
        self.llm = ChatOpenAI(api_key=openai_api_key)

    def generate_personalized_content(self, lead_data):
        prompt = PromptTemplate(
            input_variables=["lead_data"],
            template='''
Genera un resumen conciso y recomendaciones de contacto para el siguiente lead:

{lead_data}

Resumen:

Recomendaciones:
'''
        )

        chain = prompt | self.llm
        response = chain.invoke({"lead_data": lead_data})
        return response.content

class ScoringAgent:
    def calculate_score(self, lead_data):
        score = 0
        if lead_data.get('email'):
            score += 5

        if lead_data.get('company_info'):
            company_info = lead_data['company_info']
            if company_info.get('metrics') and company_info['metrics'].get('employees'):
                employees = company_info['metrics']['employees']
                if employees > 1000:
                    score += 20
                elif employees > 100:
                    score += 10
                else:
                    score += 5
            
            if company_info.get('category') and company_info['category'].get('industry'):
                score += 5

        return score

class LeadScoringSystem:
    def __init__(self, clearbit_api_key, openai_api_key):
        self.data_processor = DataProcessorAgent()
        self.enrichment_agent = DataEnrichmentAgent(api_key=clearbit_api_key)
        self.scoring_agent = ScoringAgent()
        self.personalization_agent = PersonalizationAgent(openai_api_key=openai_api_key)
        self.visualization_agent = VisualizationAgent()

    def run(self, file_path):
        df, error = self.data_processor.load_data(file_path)
        if error:
            return None, error, None

        df = self.data_processor.clean_and_normalize_data(df)
        entities = self.data_processor.identify_entities(df)

        results = []
        for _, row in df.iterrows():
            lead_data = {}
            if 'name' in entities:
                lead_data['name'] = row[entities['name']]
            if 'company' in entities:
                company_name = row[entities['company']]
                lead_data['company'] = company_name
                domain, error = self.enrichment_agent.get_company_domain(company_name)
                if domain:
                    company_info, error = self.enrichment_agent.enrich_company_data(domain)
                    if company_info:
                        lead_data['company_info'] = company_info
            if 'email' in entities:
                lead_data['email'] = row[entities['email']]

            lead_data['score'] = self.scoring_agent.calculate_score(lead_data)
            lead_data['personalized_content'] = self.personalization_agent.generate_personalized_content(lead_data)
            results.append(lead_data)

        chart_html = self.visualization_agent.generate_score_distribution_chart(results)

        return results, None, chart_html
