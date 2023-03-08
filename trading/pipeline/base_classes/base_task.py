import requests
from pipeline.configs import config


class BaseTask:
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
        r = requests.get(url=f'{config.api_base_url}/data/{self.table}?start={start}&end={end}').json()
        return r['data']

    def _db_source(self):
        db_limit = 50_000
        for i in range(self.start, self.end, db_limit * self.interval):
            batch_start = i
            batch_end = min(i + db_limit * self.interval, self.end)
            data = self._get_data(batch_start, batch_end)
            for row in data:
                yield {field: value for field, value in zip(self.fields, row)}
        
        yield None
                