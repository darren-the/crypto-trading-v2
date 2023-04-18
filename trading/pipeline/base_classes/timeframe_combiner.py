from pipeline.base_classes.task import Task
from pipeline.configs import config

class TimeframeCombiner(Task):
    def __init__(self):
        super().__init__()

    def _combine_inputs(self):
        input_elements = {}
        for input_task in self.input_tasks:
            # print(f'{input_task.task_id} {input_task.timeframe} {str(input_task.output_element)}')
            if input_task.output_element is None \
                or (self.output_element is not None and self.output_element['timestamp'] + config.base_ms != input_task.output_element['timestamp']):
                return None
            input_elements[input_task.timeframe] = input_elements.get(input_task.timeframe, {}) | input_task.output_element
        return input_elements
    