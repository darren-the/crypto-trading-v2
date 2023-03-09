class TaskOverloader:
    def __rshift__(self, other):
        if TaskOverloader in other.__class__.__mro__:
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