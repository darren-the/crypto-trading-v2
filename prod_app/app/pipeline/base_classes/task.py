import os
from app.pipeline.base_classes.base_task import BaseTask
from app.pipeline.base_classes.constants import *
from app.common.common_utils import load_config, timeframe_to_ms, date_str_to_timestamp

conf = load_config()
tasks_obj = {}

class Task(BaseTask):
    def __init__(self):
        super().__init__()
        self.env_type = os.getenv('ENV_TYPE')
        self.base_interval = timeframe_to_ms(conf["base_timeframe"])
        self.start = date_str_to_timestamp(conf["hist_start_date"])
        self.end = date_str_to_timestamp(conf["hist_end_date"])
        tasks_obj[self.task_id] = self
        self.source_output = self.generate()
        self._init_from_env_type()
        self.unpause_at_timestamp = -1
    
    def process(self, element):
        return element
    
    def generate(self):
        yield None

    def activate(self):
        if self.iteration_status != QUEUED:
            return

        if self.task_type == TASK:
            input_elements = self._combine_inputs()
            self.iteration_status = IN_PROGRESS
            self.output_element = self.process(input_elements)
            
        elif self.task_type == SOURCE:
            self.iteration_status = IN_PROGRESS
            self.output_element = self.source_output.__next__()

        # write output
        self.data_writer()

        # log task state
        if self.logging:
            self._write_log()
        
        self.iteration_status = COMPLETE

    def activate_downstream_tasks(self):
        for output_task in self.output_tasks:
            output_task.activate()
    
    def kill_all(self):
        self.output_element = None
        print(f'shutting down {self.task_id}', flush=True)
        self.data_writer(flush=True)
        self._deactivate_task()
        if self.logging:
            self._close_log()
        for output_task in self.output_tasks:
            output_task.kill_all()
    
    def _combine_inputs(self):
        # TODO: need to fix cases where one element is None but the rest aren't
        # Combine input elements into one dict
        input_elements = {}
        for input_task in self.input_tasks:
            if input_task.output_element is None \
                or (self.output_element is not None and self.output_element['timestamp'] + config.base_ms != input_task.output_element['timestamp']):
                # raise Exception(f'this should never happen. Expected timestamp = {self.output_element["timestamp"] + config.base_ms}, recieved timestamp = {input_task.output_element["timestamp"]}')
                return None
            input_elements = input_elements | input_task.output_element
        return input_elements
    
    def _init_from_env_type(self):
        if self.env_type == "local":
            self._init_local_bq()
        elif self.env_type == "dev":
            pass
        elif self.env_type == "prod":
            pass
