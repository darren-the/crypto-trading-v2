class Source:
    def __init__(self):
        self.output_element = None
        self.output_tasks = []
    
    def generate(self):
        # Should be overridden by child class
        yield 0

    def activate(self):
        for element in self.generate():
            self.output_element = element
            for output_op in self.output_tasks:
                output_op.kill_all() if element is None else output_op.activate()

    def __rshift__(self, other):
        self.output_tasks.append(other)
        other.input_tasks.append(self)
        return other
