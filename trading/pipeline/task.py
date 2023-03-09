from configs import config
import os

class Task:
    def __init__(self):
        self.output_element = None
        self.input_tasks = []
        self.output_tasks = []

        self.op_id = f'{self.symbol}.{config.table[str(type(self).__name__).lower()]}-{self.timeframe}'
        if self.write_output:
            if not os.path.exists(config.local_env_data):
                os.mkdir(config.local_env_data)
            self.file = open(f'{config.local_env_data}/{self.op_id}', 'w')
    
    def process(self, element):
        return element

    def activate(self):
        input_elements = {}
        for input_op in self.input_tasks:
            if input_op.output_element is None \
                or (self.output_element is not None and self.output_element['timestamp'] + config.base_ms != input_op.output_element['timestamp']):
                return
            input_elements = input_elements | input_op.output_element

        self.output_element = self.process(input_elements)
        if self.write_output:
            self.file.write(str(self.output_element) + '\n')

        for output_op in self.output_tasks:
            output_op.activate()
    
    def kill_all(self):
        self.output_element = None
        print(f'killing {self.op_id}')
        self.file.close()
        for output_op in self.output_tasks:
            output_op.kill_all()

    def __rshift__(self, other):
        self.output_tasks.append(other)
        other.input_tasks.append(self)
        return other
