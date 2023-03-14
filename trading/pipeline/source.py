from pipeline.base.task_overloader import TaskOverloader
from tqdm import tqdm

class Source(TaskOverloader):
    def __init__(self):
        self.output_element = None
        self.output_tasks = []
    
    def generate(self):
        # Should be overridden by child class
        yield 0

    def activate(self):
        pbar = tqdm(total=self.total)
        for element in self.generate():
            self.output_element = element
            for output_op in self.output_tasks:
                output_op.kill_all() if element is None else output_op.activate()
            pbar.update(1)
        pbar.close()
                