import requests
from pipeline.configs import config, task_config
import os


class BaseTask:
    def __init__(self):
        # task variables
        self.output_element = None
        self.output_tasks = []
        self.input_tasks = []
        self.status = task_config.UNACTIVATED
        self.task_type = task_config.TASK
        self.iteration_status = task_config.IDLE

        # logging
        if not hasattr(self, 'logging'):
            self.logging = False
        
        if self.logging:
            self._open_log()

        # data checks
        self.data_exists = False

    def __rshift__(self, other):
        if BaseTask in other.__class__.__mro__:
            self.output_tasks.append(other)
            other.input_tasks.append(self)
        elif type(other) == list:
            for output_task in other:
                self.output_tasks.append(output_task)
                output_task.input_tasks.append(self)
        return other
    
    def __rrshift__(self, other):
        if type(other) == list:
            for input_task in other:
                input_task.output_tasks.append(self)
                self.input_tasks.append(input_task)
            return self
    
    def _create_table(self):
        requests.post(
            url=f'{config.api_base_url}/create_table',
            json={
                'table': self.table,
                'schema': self.schema,
            }
        )
    
    def _db_write(self, flush=False):
        if self.output_element is not None:
            row = self.row_formatter.format(self.output_element)
            self.write_batch.append(row)
        if len(self.write_batch) >= config.max_write_batch_size or (flush and len(self.write_batch) > 0):
            self._post_data()
            self.write_batch = []
    
    def _post_data(self):
        requests.post(
            url=f'{config.api_base_url}/insert',
            json={
                'table': self.table,
                'values': self.write_batch
            }
        )
    
    def _get_data(self, start, end):
        r = requests.get(url=f'{config.api_base_url}/data/{self.table}?start={start}&end={end}&data_format=dict').json()
        return r['data']

    def _db_source(self):
        db_limit = 50_000
        for i in range(self.start, self.end, db_limit * config.base_ms):
            batch_start = i
            batch_end = min(i + db_limit * config.base_ms, self.end)
            data = self._get_data(batch_start, batch_end)
            for row in data:
                yield row
        
        yield None

    def _open_log(self):
        if not os.path.exists('pipeline_logs'):
            os.mkdir('pipeline_logs')
        self.log_file = open(f'pipeline_logs/{self.task_id}', 'w')
    
    def _write_log(self):
        self.log_file.write(str(vars(self)) + '\n')
    
    def _close_log(self):
        self.log_file.close()
    