from google.cloud import bigquery
from google.oauth2 import service_account

def get_client():
    key_path = "app/bigquery/crypto-trading-v2-key.json"
    credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(credentials=credentials, project=credentials.project_id,)

    return client

# def get_field_names_from_schema(schema):
#     return [field.name for field in schema]
