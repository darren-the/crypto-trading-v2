from pipeline.base_classes.task import tasks_obj
from pipeline.configs.task_config import ACTIVATED, SOURCE, QUEUED
from pipeline.configs import config
import os

class Source:
    def __init__(self):
        self.active_tasks = {}
        self._set_task_status()        
        self.source_tasks = {}
        self._get_source_tasks()
        self.start = int(os.getenv('PIPELINE_START'))
        self.end = int(os.getenv('PIPELINE_END')) - config.base_ms
        self.current_timestamp = self.start
        self.total_elements = (self.end - self.start) / config.base_ms
        self.elements_complete = 0
        self.percent_complete = 0

    def start_source(self):
        if len(self.active_tasks.keys()) == 0:
            return
        self._reset_iteration_status()
        while self.current_timestamp != self.end:
            self._activate_tasks()
            self.current_timestamp += config.base_ms
            self._update_progress()
            self._reset_iteration_status()
        for task_id, task in self.source_tasks.items():
            task.kill_all()

    def _reset_iteration_status(self):
        for task_id, task in self.active_tasks.items():
            task.iteration_status = QUEUED

    def _set_task_status(self):
        for task_id, task in tasks_obj.items():
            if not task.data_exists:
                task.status = ACTIVATED
                self.active_tasks[task_id] = task
                for input_task in task.input_tasks:
                    input_task.status = ACTIVATED
                    self.active_tasks[input_task.task_id] = input_task
    
    def _get_source_tasks(self):
        for task_id, task in self.active_tasks.items():
            if task.data_exists or len(task.input_tasks) == 0:
                self.source_tasks[task_id] = task
                task.task_type = SOURCE
    
    def _activate_tasks(self):
        for task_id, task in self.source_tasks.items():
            task.activate()
            if task.output_element['timestamp'] != self.current_timestamp:
                raise Exception(f'''
                    source timestamp {task.output_element["timestamp"]} 
                    of {task_id} does not match current_timstamp {self.current_timestamp}
                ''')

    def _update_progress(self):
        self.elements_complete += 1
        next_percent_complete = round(100 * self.elements_complete / self.total_elements)
        if next_percent_complete > self.percent_complete and (next_percent_complete < 100 \
            or self.elements_complete == 100):
            print(f'{str(next_percent_complete)}%', flush=True)
            self.percent_complete = next_percent_complete
    