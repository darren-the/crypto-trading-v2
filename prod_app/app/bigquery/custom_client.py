from app.bigquery.bigquery_utils import get_client
from app.common.common_utils import load_config
from google.cloud import bigquery
import time

conf = load_config("bigquery")

class CustomBigQueryClient:
    def __init__(self, logging=False):
        self.client = get_client()
        self.logging = logging

    def _log(self, message):
        if self.logging:
            print(message, flush=True)

    def _get_table_id(self, table_name):
        return f"{conf['project_id']}.{conf['dataset_id']}.{table_name}"

    def create_dataset(self, dataset_id):
        self.client.create_dataset(dataset_id)

    def check_table_exists(self, table_name):
        self._log(f"Checking table `{table_name}` exists")
        try:
            self.client.get_table(self._get_table_id(table_name))
            return True
        except:
            return False

    def create_table(self, table_name, schema):
        self._log(f"Creating table `{table_name}`")
        table = bigquery.Table(self._get_table_id(table_name), schema)
        self.client.create_table(table)
        
    def delete_table(self, table_name):
        self._log(f"Deleting table `{table_name}`")
        self.client.delete_table(self._get_table_id(table_name), not_found_ok=True)
    
    def insert_rows(self, table_name, schema, rows):
        log_msg = f"Inserting {len(rows)} rows into table `{table_name}`"
        for i in range(conf["max_retries"] + 1):
            retry_str = ""
            if i > 0:
                retry_str = f" - retry {i}"
            self._log(log_msg + retry_str)
            if i < conf["max_retries"]:
                try:
                    self._insert_rows(table_name, schema, rows)
                    break
                except:
                    time.sleep(2)
            else:
                self._insert_rows(table_name, schema, rows)

    def _insert_rows(self, table_name, schema, rows):
        self.client.insert_rows(
            table=bigquery.Table(self._get_table_id(table_name), schema),
            rows=rows,
            selected_fields=schema
        )