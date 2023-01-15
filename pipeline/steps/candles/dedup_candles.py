import apache_beam as beam

class DedupCandles(beam.DoFn):
    def __init__(self):
        self.last_timestamp = None

    def process(self, element):  
        if self.last_timestamp is not None and self.last_timestamp == element['timestamp']:
            return
        
        self.last_timestamp = element['timestamp']
        yield element
