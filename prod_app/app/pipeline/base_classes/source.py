from app.pipeline.base_classes.task import tasks_obj
from app.pipeline.base_classes.constants import *
from app.common.common_utils import timeframe_to_ms, load_config, date_str_to_timestamp
from copy import deepcopy


conf = load_config()

class Source:
    def __init__(self):
        self.active_tasks = {}
        self._init_task_status()        
        self.source_tasks = {}
        self._init_source_tasks()
        self.task_metrics = {task.task_id: {} for task in tasks_obj.values()}
        self.base_interval = timeframe_to_ms(conf["base_timeframe"])
        self.start = date_str_to_timestamp(conf["hist_start_date"])
        self.end = date_str_to_timestamp(conf["hist_end_date"])
        self.current_timestamp = self.start
        self.total_elements = (self.end - self.start) / self.base_interval
        self.elements_complete = 0
        self.percent_complete = 0

    def start_source(self):
        print("starting")
        if len(self.active_tasks.keys()) == 0:
            return
        self._init_iteration_status()
        while self.current_timestamp < self.end:
            self._activate_tasks()
            self._update_progress()
            self._reset_iteration_status()
            self.current_timestamp += self.base_interval
        for task_id, task in self.source_tasks.items():
            task.kill_all()
        self._summarise_task_metrics()

    def _init_iteration_status(self):
        for task_id, task in self.active_tasks.items():
            if task.status == ACTIVATED:
                task.iteration_status = QUEUED

    def _reset_iteration_status(self):
        # Reset the iteration status of all active tasks
        # NOTE: MUST BE RAN BEFORE ITERATING current_timestamp
        for task_id, task in self.active_tasks.items():
            if task.status == ACTIVATED and task.iteration_status == COMPLETE:
                task.iteration_status = QUEUED

    def _init_task_status(self):
        for task_id, task in tasks_obj.items():
            task.status = ACTIVATED
            self.active_tasks[task_id] = task
            for input_task in task.input_tasks:
                input_task.status = ACTIVATED
                self.active_tasks[input_task.task_id] = input_task
    
    def _init_source_tasks(self):
        for task_id, task in self.active_tasks.items():
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
            self._toggle_paused_task(task_id, task)
            task.activate_downstream_tasks()

    def _toggle_paused_task(self, task_id, task):
        if task.output_element is not None \
            and task.output_element['timestamp'] > self.current_timestamp:
            task.iteration_status = PAUSED
            task.unpause_at_timestamp = task.output_element['timestamp']
            self._impute_none(task)
            self._update_task_metric_count(task_id, "missing_timestamps")
        elif self.current_timestamp == task.unpause_at_timestamp:
            task.iteration_status == QUEUED
            task.output_element = deepcopy(task.stored_output_element)
        elif task.output_element is not None \
            and task.output_element["timestamp"] < self.current_timestamp:
            raise Exception(f'''
                source timestamp {task.output_element["timestamp"]} 
                of {task_id} is behind current_timstamp {self.current_timestamp}
            ''')
    
    def _impute_none(self, task):
        task.stored_output_element = deepcopy(task.output_element)
        task.output_element = None

    def _update_progress(self):
        self.elements_complete += 1
        next_percent_complete = round(100 * self.elements_complete / self.total_elements)
        if next_percent_complete > self.percent_complete and (next_percent_complete < 100 \
            or self.elements_complete == 100):
            print(f'{str(next_percent_complete)}%', flush=True)
            self.percent_complete = next_percent_complete
    
    def _summarise_task_metrics(self):
        summary_str = f"Task metrics summary\n{'-' * 20}\n"
        summary_str_len = len(summary_str) # track whether there is anything to summarise
        for task_id, metrics in self.task_metrics.items():
            if len(metrics.keys()) > 0:
                summary_str += task_id + "\n"
                for metric_name, metric_value in metrics.items():
                    summary_str += f"> {metric_name} = {metric_value}\n"
                summary_str += "-" * 20 + "\n"
        
        if len(summary_str) > summary_str_len:
            print(summary_str)

    def _update_task_metric_count(self, task_id, metric_name):
        self.task_metrics[task_id][metric_name] = self.task_metrics[task_id].get(metric_name, 0) + 1
