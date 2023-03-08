class Operator:
    def __init__(self):
        self.output_element = None
        self.input_operators = []
        self.output_operators = []
    
    def process(self, element):
        # Should be overridden by child class
        return element

    def activate(self):
        input_elements = {}
        for input_op in self.input_operators:
            if input_op.output_element is None \
                or (self.output_element is not None and self.output_element['timestamp'] >= input_op.output_element['timestamp']):
                return
            input_elements = input_elements | input_op.output_element

        self.output_element = self.process(input_elements)

        for output_op in self.output_operators:
            output_op.activate()

    def __rshift__(self, other):
        self.output_operators.append(other)
        other.input_operators.append(self)
