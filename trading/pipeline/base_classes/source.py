from pipeline.base_classes.base_task import BaseTask
from pipeline.configs import config
from pipeline.utils.row_formatters import Psycopg2Formatter
import os
import requests

class Source(BaseTask):
    def __init__(self):
        self.output_element = None
        self.output_tasks = []

        # Metadata
        self.task_name = str(type(self).__name__).lower()
        self.task_id = f'{self.symbol}_{self.task_name}'
        self.table = f'{self.symbol}_{config.table[self.task_name]}'
        self.schema = config.schema[self.task_name]

        # Writing
        self.write_batch = []
        self.row_formatter = Psycopg2Formatter(self.task_name)

        # Progress tracking
        self.total_elements = (self.end - self.start) / self.interval
        self.elements_complete = 0
        self.percent_complete = 0
        
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
            if element is not None and self.output_element is not None \
                and element['timestamp'] != self.output_element['timestamp'] + config.base_ms:
                raise Exception(
                    f'''
                    Error: expected timestamp {str(self.output_element["timestamp"] + config.base_ms)} 
                    but received {str(self.element['timestamp'])}
                    '''
                )
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
            
            # Print progress
            self.elements_complete += 1
            next_percent_complete = round(100 * self.elements_complete / self.total_elements)
            if next_percent_complete > self.percent_complete and (next_percent_complete < 100 \
                or self.elements_complete == 100):
                print(f'{str(next_percent_complete)}%', flush=True)
                self.percent_complete = next_percent_complete
    
    def _post_data(self):
        # requests.post(
        #     url=f'{config.api_base_url}/insert',
        #     json={
        #         'table': self.table,
        #         'values': self.write_batch
        #     }
        # )
        pass  # temporarily to avoid overwriting. will be reverted once reading from base candles is supported
                