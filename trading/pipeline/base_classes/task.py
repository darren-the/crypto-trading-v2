from pipeline.configs import config, task_config
import os
from pipeline.base_classes.base_task import BaseTask
from pipeline.utils.row_formatters import Psycopg2Formatter
import requests

tasks_obj = {}

class Task(BaseTask):
    def __init__(self):
        super().__init__()

        # TODO: properly set task_id and table dynamically based on whether symbol, timeframe and pipeline_id exists
        # pipeline_id always exists so an ignore parameter may needed for this to work
        self.task_name = str(type(self).__name__).lower()
        self.task_id = f'{self.symbol}_{self.task_name}'.lower()
        self.table = f'{self.symbol}_{config.table[self.task_name]}'.lower()
        if 'timeframe' in self.__dict__.keys():
            self.task_id += f'_{self.timeframe}'.lower()
            self.table += f'_{self.timeframe}'.lower()
        else:
            self.timeframe = 'no_timeframe'
        if 'ignore_pipeline_id' not in self.__dict__.keys() or not self.ignore_pipeline_id:
            self.task_id += f'_{os.getenv("PIPELINE_ID")}'.lower()
            self.table += f'_{os.getenv("PIPELINE_ID")}'.lower()
        self.schema = config.schema[self.task_name]
        self.fields = [s.split(' ')[0] for s in self.schema]
        self.env_type = os.getenv('ENV_TYPE')
        self.start = int(os.getenv('PIPELINE_START'))
        self.end = int(os.getenv('PIPELINE_END')) - config.base_ms
        tasks_obj[self.task_id] = self

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
                    self.data_source = self._db_source()
                    self.data_exists = True
                else:
                    # if the data doesn't exist yet then write to db
                    self.data_writer = self._db_write
                    self._create_table()
            else:
                # also write if table doesn't exist
                self.data_writer = self._db_write
                self._create_table()
    
    def process(self, element):
        return element
    
    def generate(self):
        yield None

    def activate(self):
        if self.iteration_status != task_config.QUEUED:
            return

        if self.task_type == task_config.TASK:
            input_elements = self._combine_inputs()
            if input_elements is None:
                return
            self.iteration_status = task_config.IN_PROGRESS
            self.output_element = self.process(input_elements)
            
        elif self.task_type == task_config.SOURCE:
            self.iteration_status = task_config.IN_PROGRESS
            self.output_element = self.data_source.__next__()

        # write output
        self.data_writer()

        # log task state
        if self.logging:
            self._write_log()
        
        self.iteration_status = task_config.COMPLETE

        for output_task in self.output_tasks:
            output_task.activate()
    
    def kill_all(self):
        if self.status == task_config.ACTIVATED:
            self.output_element = None
            print(f'shutting down {self.task_id}', flush=True)
            self.data_writer(flush=True)
            self.status = task_config.DEACTIVATED
            self.iteration_status = task_config.IDLE
            if self.logging:
                self._close_log()
            for output_task in self.output_tasks:
                output_task.kill_all()

    def convert_data_source_to_generator(self):
        if not self.data_exists:
            self.data_source = self.generate()
    
    def _combine_inputs(self):
        # Combine input elements into one dict
        input_elements = {}
        for input_task in self.input_tasks:
            if input_task.output_element is None \
                or (self.output_element is not None and self.output_element['timestamp'] + config.base_ms != input_task.output_element['timestamp']):
                # raise Exception(f'this should never happen. Expected timestamp = {self.output_element["timestamp"] + config.base_ms}, recieved timestamp = {input_task.output_element["timestamp"]}')
                return None
            input_elements = input_elements | input_task.output_element
        return input_elements
