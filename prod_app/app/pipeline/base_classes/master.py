from app.pipeline.base_classes.task import tasks_obj
from app.pipeline.base_classes.constants import *
from app.common.common_utils import timeframe_to_ms, load_config, date_str_to_timestamp
from copy import deepcopy


conf = load_config()

class Master:
    def __init__(self):   
        self.source_tasks = {}
        self._init_source_tasks()
        self.base_interval = timeframe_to_ms(conf["base_timeframe"])
        self.start = date_str_to_timestamp(conf["hist_start_date"])
        self.end = date_str_to_timestamp(conf["hist_end_date"])
        self.current_timestamp = self.start
        self.total_elements = (self.end - self.start) / self.base_interval
        self.elements_complete = 0
        self.percent_complete = 0

    def start_pipeline(self):
        print("starting")
        self._init_iteration_status()
        while self.current_timestamp < self.end:
            self._activate_tasks()
            self._update_progress()
            self._reset_iteration_status()
            self.current_timestamp += self.base_interval
        for task_id, task in self.source_tasks.items():
            task.kill_all()

    def _init_iteration_status(self):
        for task_id, task in tasks_obj.items():
            task.iteration_status = QUEUED

    def _reset_iteration_status(self):
        # Reset the iteration status of all active tasks
        for task_id, task in tasks_obj.items():
            if task.iteration_status == COMPLETE:
                task.iteration_status = QUEUED
    
    def _init_source_tasks(self):
        for task_id, task in tasks_obj.items():
            if len(task.input_tasks) == 0:
                self.source_tasks[task_id] = task
                task.task_type = SOURCE
    
    def _activate_tasks(self):
        for task_id, task in self.source_tasks.items():
            try:
                task.activate()
            except:
                # print(self.current_timestamp, self.end)
                print(task_id, self.current_timestamp)
                raise Exception("noooo")
            task.activate_downstream_tasks()

    def _update_progress(self):
        self.elements_complete += 1
        next_percent_complete = round(100 * self.elements_complete / self.total_elements)
        if next_percent_complete > self.percent_complete and (next_percent_complete < 100 \
            or self.elements_complete == 100):
            print(f'{str(next_percent_complete)}%', flush=True)
            self.percent_complete = next_percent_complete
