
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

class BigQueryTool:
    def __init__(self, credentials_path: str):
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.client = bigquery.Client(credentials=self.credentials, project=self.credentials.project_id)

    def run_query(self, query: str) -> pd.DataFrame:
        """
        Runs a SQL query on BigQuery and returns the results as a Pandas DataFrame.
        """
        try:
            query_job = self.client.query(query)
            results = query_job.to_dataframe()
            return results
        except Exception as e:
            print(f"Error running BigQuery query: {e}")
            raise
