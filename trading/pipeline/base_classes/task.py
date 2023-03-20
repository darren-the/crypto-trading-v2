from pipeline.configs import config
import os
from pipeline.base_classes.base_task import BaseTask
from pipeline.utils.row_formatters import Psycopg2Formatter
import requests


class Task(BaseTask):
    def __init__(self):
        self.output_element = None
        self.input_tasks = []
        self.output_tasks = []

        # metadata
        self.task_name = str(type(self).__name__).lower()
        self.task_id = f'{self.symbol}_{self.task_name}_{self.timeframe}_{os.getenv("PIPELINE_ID")}'.lower()
        self.table = f'{self.symbol}_{config.table[self.task_name]}_{self.timeframe}_{os.getenv("PIPELINE_ID")}'.lower()
        self.schema = config.schema[self.task_name]
        self.fields = [s.split(' ')[0] for s in self.schema]
        self.env_type = os.getenv('ENV_TYPE')
        self.start = int(os.getenv('PIPELINE_START'))
        self.end = int(os.getenv('PIPELINE_END')) - config.base_ms

        # writing
        self.write_batch = []
        self.row_formatter = Psycopg2Formatter(self.task_name)
        def default_writer(*args, **kwargs):
            return
        self.data_writer = default_writer
        if self.env_type == 'dev':
            table_exists = requests.get(url=f'{config.api_base_url}/exists?table={self.table}').json()['data']
            if table_exists:
                datarange = requests.get(url=f'{config.api_base_url}/datarange?table={self.table}').json()['data']
                if self.start >= int(datarange[0]) and self.end <= int(datarange[-1] + config.base_ms):
                    pass  # something did happen here before but then it got changed. too lazy to refactor the if statements.
                else:
                    # if the data doesn't exist yet then write to db
                    self.data_writer = self._db_write
                    self._create_table()
            else:
                # also write if table doesn't exist
                self.data_writer = self._db_write
                self._create_table()

        super().__init__()
    
    def process(self, element):
        return element

    def activate(self):
        input_elements = {}

        # Combine input elements into one dict
        for input_task in self.input_tasks:
            if input_task.output_element is None \
                or (self.output_element is not None and self.output_element['timestamp'] + config.base_ms != input_task.output_element['timestamp']):
                # raise Exception(f'this should never happen. Expected timestamp = {self.output_element["timestamp"] + config.base_ms}, recieved timestamp = {input_task.output_element["timestamp"]}')
                return
            input_elements = input_elements | input_task.output_element

        self.output_element = self.process(input_elements)
        
        # write output
        self.data_writer()

        # log task state
        if self.logging:
            self._write_log()

        for output_op in self.output_tasks:
            output_op.activate()
    
    def kill_all(self):
        self.output_element = None
        print(f'shutting down {self.task_id}', flush=True)
        self.data_writer(flush=True)
        if self.logging:
            self._close_log()
        for output_op in self.output_tasks:
            output_op.kill_all()
