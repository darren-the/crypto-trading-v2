import requests
from pipeline.configs import config, task_config
import os
from pipeline.utils.row_formatters import psycopg2_format


class BaseTask:
    def __init__(self):
        
        # task variables
        self._init_table_variables()
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
    
    def _create_table(self, table, schema):
        requests.post(
            url=f'{config.api_base_url}/create_table',
            json={
                'table': table,
                'schema': schema,
            }
        )
    
    def _db_write(self, flush=False):
        if self.output_element is not None:
            row = psycopg2_format(self.output_element, self.fields)
            self.write_batch.append(row)
            for extra_output_name in self.extra_output_names:
                for element in self.output_element[extra_output_name]:
                    extra_row = psycopg2_format(element, self.extra_fields[extra_output_name])
                    self.extra_write_batches[extra_output_name].append(extra_row)
        if len(self.write_batch) >= config.max_write_batch_size or (flush and len(self.write_batch) > 0):
            self._post_data(self.table, self.write_batch)
            self.write_batch = []
        for extra_output_name in self.extra_output_names:
            if len(self.extra_write_batches[extra_output_name]) >= config.max_write_batch_size \
                or (flush and len(self.extra_write_batches[extra_output_name]) > 0):
                self._post_data(
                    self.extra_tables[extra_output_name],
                    self.extra_write_batches[extra_output_name]
                )
    
    def _post_data(self, table, values):
        requests.post(
            url=f'{config.api_base_url}/insert',
            json={
                'table': table,
                'values': values,
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

    def _init_table_variables(self):
        if not 'extra_output_names' in self.__dict__.keys():
            self.extra_output_names = []
        self.task_name = str(type(self).__name__).lower()
        if 'symbol' in self.__dict__.keys():
            symbol_prefix = f'{self.symbol}_'.lower()
        else:
            symbol_prefix = ''
            
        self.task_id = f'{symbol_prefix}{self.task_name}'.lower()
        self.table = f'{symbol_prefix}{config.table[self.task_name]}'.lower()
        self.extra_tables = {}
        self.extra_write_batches = {}
        for extra_output_name in self.extra_output_names:
            self.extra_tables[extra_output_name] = f'{symbol_prefix}{extra_output_name}'.lower()
            self.extra_write_batches[extra_output_name] = []
        if 'timeframe' in self.__dict__.keys():
            self.task_id += f'_{self.timeframe}'.lower()
            self.table += f'_{self.timeframe}'.lower()
            for extra_output_name in self.extra_output_names:
                self.extra_tables[extra_output_name] += f'_{self.timeframe}'.lower()
        else:
            self.timeframe = 'no_timeframe'
        if 'ignore_pipeline_id' not in self.__dict__.keys() or not self.ignore_pipeline_id:
            self.task_id += f'_{os.getenv("PIPELINE_ID")}'.lower()
            self.table += f'_{os.getenv("PIPELINE_ID")}'.lower()
            for extra_output_name in self.extra_output_names:
                self.extra_tables[extra_output_name] += f'_{os.getenv("PIPELINE_ID")}'.lower()
        self.schema = config.schema[self.task_name]
        self.fields = [s.split(' ')[0] for s in self.schema]
        self.extra_schemas = {}
        self.extra_fields = {}
        for extra_output_name in self.extra_output_names:
            self.extra_schemas[extra_output_name] = config.schema[extra_output_name]
            self.extra_fields[extra_output_name] = [s.split(' ')[0] for s in self.extra_schemas[extra_output_name]]
    