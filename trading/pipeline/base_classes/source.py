from pipeline.base_classes.task_overloader import TaskOverloader
from pipeline.configs import config
from tqdm import tqdm
import os
import requests

class Source(TaskOverloader):
    def __init__(self):
        self.output_element = None
        self.output_tasks = []
        self.write_batch = []
        self.class_name = str(type(self).__name__).lower()
        self.table_name = config.table[self.class_name]
        self.schema = config.schema[self.class_name]
        self.task_id = f'{self.symbol}.{self.table_name}'
    
    def generate(self):
        # Should be overridden by child class
        yield 0

    def activate(self):
        pbar = tqdm(total=self.total)

        env_type = os.getenv('ENV_TYPE')
        if env_type == 'dev':
            requests.post(
                url=f'{config.api_base_url}/create_table',
                data={
                    'table_name': self.table_name,
                    'schema': self.schema,
                }
            )

        for element in self.generate():
            self.output_element = element
            
            # write output
            # if element is not None:
            #     self.write_batch.append(element)
            # if len(self.write_batch) > config.max_write_batch_size:
            #     pass
                
            for output_op in self.output_tasks:
                output_op.kill_all() if element is None else output_op.activate()
            pbar.update(1)
        pbar.close()
                