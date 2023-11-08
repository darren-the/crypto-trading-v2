import requests
import os
from app.bigquery.client import bq_client
from app.bigquery.schemas import schemas
from app.common.common_utils import load_config
from app.pipeline.base_classes.constants import *

conf = load_config()
bq_init_check = set()

class BaseTask:
    def __init__(self):
        
        # task variables
        self.task_name = self._get_task_name()
        self.task_id = self._get_task_id()
        self.table_name = self._get_table_name()
        self.output_element = None
        self.output_tasks = []
        self.input_tasks = []
        self.status = UNACTIVATED
        self.task_type = TASK  # default
        self.iteration_status = IDLE

        # writing
        self.write_batch = []
        self.data_writer = self._default_writer

        # logging
        if not hasattr(self, 'logging'):
            self.logging = False
        
        if self.logging:
            self._open_log()

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
                self.extra_write_batches[extra_output_name] = []
    
    def _post_data(self, table, values):
        print(f'post insert to {table}', flush=True)
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

    def _get_table_name(self):
        if "table_name" in self.__dict__.keys():
            return self.table_name
        return self._get_task_name()

    def _get_task_name(self):
        return str(type(self).__name__)

    def _get_task_id(self):
        task_id_attributes = [
            self._get_task_symbol(),
            self._get_task_timeframe(),
        ]
        task_id_attributes = [att for att in task_id_attributes if att != ""]
        task_id = self._get_task_name() + "_" + "_".join(task_id_attributes)
        return task_id

    def _get_task_symbol(self):
        if "symbol" in self.__dict__.keys():
            return self.symbol
        else:
            return ""

    def _get_task_timeframe(self):
        if "timeframe" in self.__dict__.keys():
            return self.timeframe
        else:
            return ""

    def _OLD_init_table_variables(self):
        """
        Defines:
            - extra_output_names
            - task_name
            - task_id
            - table
            - extra_tables
            - extra_write_batches
            - timeframe
            - schema
            - fields
            - extra_schemas
            - extra_fields
        """
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
    
    def _default_writer(*args, **kwargs):
        return

    def _init_local_bq(self):
        # init table if not yet done
        if self.task_name not in bq_init_check:
            bq_client.delete_table(self.table_name)
            bq_client.create_table(self.table_name, schemas[self.task_name])
            # bq_client.check_table_exists(self.table_name)  # need to run this
            bq_init_check.add(self.task_name)
        self.data_writer = self._bq_write

    def _bq_write(self, flush=False):
        if self.output_element is not None:
            self.write_batch.append(self.output_element)       
        if len(self.write_batch) >= conf["max_write_batch_size"] or (flush and len(self.write_batch) > 0):
            bq_client.insert_rows(self.table_name, schemas[self.task_name], self.write_batch)
            self.write_batch = []
        
    def _deactivate_task(self):
        self.status = DEACTIVATED
        self.iteration_status = IDLE
        