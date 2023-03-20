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
        self.table = f'{self.symbol}_{config.table[self.task_name]}'.lower()
        self.schema = config.schema[self.task_name]
        self.fields = [s.split(' ')[0] for s in self.schema]
        self.env_type = os.getenv('ENV_TYPE')
        self.start = int(os.getenv('PIPELINE_START'))
        self.end = int(os.getenv('PIPELINE_END'))

        # Progress tracking
        self.total_elements = (self.end - self.start) / config.base_ms
        self.elements_complete = 0
        self.percent_complete = 0

        # reading/writing
        self.write_batch = []
        self.row_formatter = Psycopg2Formatter(self.task_name)
        self.data_source = []
        def default_writer(*args, **kwargs):
            return
        self.data_writer = default_writer
        if self.env_type == 'dev':
            table_exists = requests.get(url=f'{config.api_base_url}/exists?table={self.table}').json()['data']
            if table_exists:
                datarange = requests.get(url=f'{config.api_base_url}/datarange?table={self.table}').json()['data']
                if self.start >= int(datarange[0]) and self.end <= int(datarange[-1] + config.base_ms):
                    # if the data already exists then read from the database
                    # and don't write
                    self.data_source = self._db_source()
                else:
                    # if the data doesn't exist yet then fetch from exchange api
                    # and write to database
                    self.data_source = self.generate()
                    self.data_writer = self._db_write
                    self._create_table()
            else:
                # also fetch/write to db if the table doesn't exist yet
                self.data_source = self.generate()
                self.data_writer = self._db_write
                self._create_table()
                
        super().__init__()
        
    def generate(self):
        # Should be overridden by child class
        yield 0

    def activate(self):  
        for element in self.data_source:
            if element is not None and self.output_element is not None \
                and element['timestamp'] != self.output_element['timestamp'] + config.base_ms:
                raise Exception(
                    f'''
                    Error: expected timestamp {str(self.output_element["timestamp"] + config.base_ms)} 
                    but received {str(self.element['timestamp'])}
                    '''
                )
            self.output_element = element

            # write output
            self.data_writer()

            # log source state
            if self.logging:
                self._write_log()
            
            # Print progress
            self.elements_complete += 1
            next_percent_complete = round(100 * self.elements_complete / self.total_elements)
            if next_percent_complete > self.percent_complete and (next_percent_complete < 100 \
                or self.elements_complete == 100):
                print(f'{str(next_percent_complete)}%', flush=True)
                self.percent_complete = next_percent_complete
            
            for output_op in self.output_tasks:
                if element is None:
                    self.data_writer(flush=True)
                    if self.logging:
                        self._close_log()
                    print(f'{self.table} has been flushed')
                    output_op.kill_all()
                else:
                    output_op.activate()
            