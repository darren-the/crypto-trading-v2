from pipeline.configs import config
import os
from pipeline.base_classes.base_task import BaseTask


class Task(BaseTask):
    def __init__(self):
        self.output_element = None
        self.input_tasks = []
        self.output_tasks = []
        self.file = None
        self.task_name = str(type(self).__name__).lower()
        self.task_id = f'{self.symbol}_{self.task_name}_{self.timeframe}'
        self.table = f'{self.symbol}_{config.table[self.task_name]}_{self.timeframe}'
        self.schema = config.schema[self.task_name]
    
    def process(self, element):
        return element

    def activate(self):
        if self.file is None:
            if self.write_output:
                if not os.path.exists(config.local_env_data):
                    os.mkdir(config.local_env_data)
                self.file = open(f'{config.local_env_data}/{self.table}', 'w')
        input_elements = {}
        for input_op in self.input_tasks:
            if input_op.output_element is None \
                or (self.output_element is not None and self.output_element['timestamp'] + config.base_ms != input_op.output_element['timestamp']):
                return
            input_elements = input_elements | input_op.output_element

        self.output_element = self.process(input_elements)
        if self.write_output:
            self.file.write(str(self.output_element) + '\n')

        for output_op in self.output_tasks:
            output_op.activate()
    
    def kill_all(self):
        self.output_element = None
        print(f'shutting down {self.task_id}', flush=True)
        self.file.close()
        for output_op in self.output_tasks:
            output_op.kill_all()
