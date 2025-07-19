
from langchain_core.tools import tool
import os
import numpy as np
import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest, OrderBy
)

# Configuración de credenciales y cliente
base_dir = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(base_dir, '..' , 'static', 'ga4-apponepum.json')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

ga_client = BetaAnalyticsDataClient()

@tool
def get_daily_traffic(property_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Obtiene el tráfico diario de GA4.
    """
    try:
        request = RunReportRequest(
            property=f'properties/{property_id}',
            date_ranges=[DateRange(
                start_date=start_date,
                end_date=end_date
            )],
            dimensions=[Dimension(name='date')],
            metrics=[
                Metric(name='sessions'),
                Metric(name='activeUsers'),
                Metric(name='newUsers'),
                Metric(name='screenPageViews')
            ]
        )
        
        response = ga_client.run_report(request=request)
        
        rows = []
        for row in response.rows:
            rows.append({
                'date': row.dimension_values[0].value,
                'sessions': int(row.metric_values[0].value),
                'activeUsers': int(row.metric_values[1].value),
                'newUsers': int(row.metric_values[2].value),
                'pageviews': int(row.metric_values[3].value)
            })
            
        df = pd.DataFrame(rows)
        df['date'] = pd.to_datetime(df['date'])
        return df
        
    except Exception as e:
        raise ValueError(f"Error en get_daily_traffic: {str(e)}")

@tool
def get_medium_traffic(property_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Obtiene el tráfico por medio"""
    try:
        request = RunReportRequest(
            property='properties/' + property_id,
            dimensions=[Dimension(name="sessionMedium")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
        )
        response = ga_client.run_report(request=request)
        rows = []
        for row in response.rows:
            rows.append({
                'sessionMedium': row.dimension_values[0].value,
                'activeUsers': int(row.metric_values[0].value)
            })
        df = pd.DataFrame(rows)
        return df
    except Exception as e:
        raise ValueError(f"Error al obtener datos de medio: {str(e)}")

@tool
def get_top_pages(property_id: str, start_date: str, end_date: str) -> list:
    """Obtiene las páginas más visitadas"""
    try:
        request = RunReportRequest(
            property='properties/' + property_id,
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="activeUsers")],
            order_bys=[OrderBy(metric={'metric_name': 'activeUsers'}, desc=True)],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
        )
        response = ga_client.run_report(request=request)
        rows = []
        for row in response.rows:
            rows.append({
                'pagePath': row.dimension_values[0].value,
                'activeUsers': int(row.metric_values[0].value)
            })
        df = pd.DataFrame(rows)
        return df.head(10).to_dict('records')
    except Exception as e:
        raise ValueError(f"Error al obtener páginas principales: {str(e)}")

@tool
def get_regions_traffic(property_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Obtiene el tráfico por región"""
    try:
        request = RunReportRequest(
            property='properties/' + property_id,
            dimensions=[Dimension(name="country")],
            metrics=[Metric(name="activeUsers")],
            order_bys=[OrderBy(metric={'metric_name': 'activeUsers'}, desc=True)],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
        )
        response = ga_client.run_report(request=request)
        rows = []
        for row in response.rows:
            rows.append({
                'country': row.dimension_values[0].value,
                'activeUsers': int(row.metric_values[0].value)
            })
        df = pd.DataFrame(rows)
        return df.head(10)
    except Exception as e:
        raise ValueError(f"Error al obtener datos de regiones: {str(e)}")
