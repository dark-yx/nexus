import numpy as np
import pandas as pd
from google.oauth2.credentials import Credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns

def get_google_analytics_properties(credentials_dict):
    try:
        credentials = Credentials(
            token=credentials_dict['access_token'],
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri=credentials_dict.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=credentials_dict['client_id'],
            client_secret=credentials_dict['client_secret']
        )

        data_client = BetaAnalyticsDataClient(credentials=credentials)
        properties = data_client.list_properties().properties
        property_info = [(property.name, property.display_name, property.create_time) for property in properties]

        return property_info
    except Exception as e:
        raise ValueError(f"Error al obtener las propiedades de Google Analytics: {e}")


def generate_analytics_report(credentials_dict, property_id, start_date, end_date):
    try:
        credentials = Credentials(
            token=credentials_dict['access_token'],
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri=credentials_dict.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=credentials_dict['client_id'],
            client_secret=credentials_dict['client_secret']
        )

        data_client = BetaAnalyticsDataClient(credentials=credentials)

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="month"), Dimension(name="sessionMedium")],
            metrics=[Metric(name="averageSessionDuration"), Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        )

        response = data_client.run_report(request)

        return response
        
    except Exception as e:
        raise ValueError(f"Error al generar el informe de Google Analytics: {e}")


def process_report_response(response):
    """Process the report response."""
    report_data = {}
    
    report_data['row_count'] = response.row_count
    report_data['dimension_headers'] = [dimension.name for dimension in response.dimension_headers]
    report_data['metric_headers'] = [metric.name for metric in response.metric_headers]
    report_data['rows'] = []
    
    for row in response.rows:
        row_data = {}
        for i, dimension_value in enumerate(row.dimension_values):
            row_data[report_data['dimension_headers'][i]] = dimension_value.value

        for i, metric_value in enumerate(row.metric_values):
            row_data[report_data['metric_headers'][i]] = metric_value.value

        report_data['rows'].append(row_data)
    
    return report_data

def plot_report_data(report_data, metric_name):
    """Plot report data."""
    df = pd.DataFrame(report_data['rows'])
    df['date'] = pd.to_datetime(df['date'])
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='date', y=metric_name)
    plt.title(f'{metric_name} Over Time')
    plt.xlabel('Date')
    plt.ylabel(metric_name)
    plt.xticks(rotation=45)
    plt.show()

def main(credentials_dict):
    try:
        properties = get_google_analytics_properties(credentials_dict)
        print("Propiedades de Google Analytics:")
        for idx, prop in enumerate(properties):
            print(f"{idx + 1}. Nombre: {prop[1]}, ID: {prop[0]}, Creado: {prop[2]}")

        property_id = input("Seleccione el ID de la propiedad para generar el informe: ")
        start_date = input("Ingrese la fecha de inicio (YYYY-MM-DD): ")
        end_date = input("Ingrese la fecha de fin (YYYY-MM-DD): ")

        response = generate_analytics_report(credentials_dict, property_id, start_date, end_date)
        report_data = process_report_response(response)
        
        # Plot active users over time
        plot_report_data(report_data, 'activeUsers')
        
        # Plot average session duration over time
        plot_report_data(report_data, 'averageSessionDuration')

        return report_data

    except Exception as e:
        raise ValueError(f"Error: {e}")

