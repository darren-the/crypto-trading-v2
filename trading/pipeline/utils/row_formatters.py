from pipeline.configs import config

class Psycopg2Formatter:
    def __init__(self, task_name):
        self.field_order = [s.split(' ')[0] for s in config.schema[task_name]]
    
    def format(self, element):
        row = str(tuple(element[field] for field in self.field_order))
        return row
        
def psycopg2_format(element, fields):
    return str(tuple(element[field] for field in fields))
