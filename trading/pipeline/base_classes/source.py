from pipeline.base_classes.base_task import BaseTask
from pipeline.configs import config
from pipeline.utils.row_formatters import Psycopg2Formatter
import os
import requests

class Source(BaseTask):
    def __init__(self):
        self.output_element = None
        self.output_tasks = []
        self.write_batch = []
        self.task_name = str(type(self).__name__).lower()
        self.task_id = f'{self.symbol}_{self.task_name}'
        self.table = f'{self.symbol}_{config.table[self.task_name]}'
        self.schema = config.schema[self.task_name]
        self.row_formatter = Psycopg2Formatter(self.task_name)
        
    def generate(self):
        # Should be overridden by child class
        yield 0

    def activate(self):
        env_type = os.getenv('ENV_TYPE')
        if env_type == 'dev':
            requests.post(
                url=f'{config.api_base_url}/create_table',
                json={
                    'table': self.table,
                    'schema': self.schema,
                }
            )

        for element in self.generate():
            self.output_element = element
            
            # write output to database
            if env_type == 'dev':
                if element is None:
                    # No more elements. flush out remaining data
                    self._post_data()
                else:
                    row = self.row_formatter.format(element)
                    self.write_batch.append(row)
                if len(self.write_batch) >= config.max_write_batch_size:
                    self._post_data()
                    self.write_batch = []
                
            for output_op in self.output_tasks:
                output_op.kill_all() if element is None else output_op.activate()
    
    def _post_data(self):
        requests.post(
            url=f'{config.api_base_url}/insert',
            json={
                'table': self.table,
                'values': self.write_batch
            }
        )
                