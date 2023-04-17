from pipeline.base_classes.task import Task


class AvgRSI(Task):
    def __init__(self, *args, **kwargs):
        self.avg_rsi_length = 5
        self.scale_upper_bound = 70
        self.scale_lower_bound = 30
        self.scale_factor = -1
        self.__dict__.update(kwargs)
        self.rsi_elements = []
        super().__init__()

        if self.scale_factor >= 1:
            raise Exception(f'{self.task_id}: scale_factor must be between 0 and 1')
        
    def process(self, element):
        avg_rsi = -1
        if len(self.rsi_elements) == 0:
            self.rsi_elements.append(element)
        elif element['candle_timestamp'] == self.rsi_elements[-1]['candle_timestamp']:
            self.rsi_elements[-1] = element
        else:
            self.rsi_elements.append(element)
        
        if len(self.rsi_elements) > self.avg_rsi_length:
            self.rsi_elements.pop(0)
        
        if len(self.rsi_elements) == self.avg_rsi_length:
            sum_rsi = 0
            for rsi_element in self.rsi_elements:
                if self.scale_factor != -1 and rsi_element['rsi'] <= self.scale_lower_bound:
                    sum_rsi += rsi_element['rsi'] * (1 - self.scale_factor)
                elif self.scale_factor != -1 and rsi_element['rsi'] >= self.scale_upper_bound:
                    sum_rsi += rsi_element['rsi'] * (1 + self.scale_factor)
                else:
                    sum_rsi += rsi_element['rsi']
            avg_rsi = sum_rsi / self.avg_rsi_length
    
        return {
            'timestamp': element['timestamp'],
            'candle_timestamp': element['candle_timestamp'],
            'avg_rsi': round(avg_rsi, 2),
            'is_complete': element['is_complete'],
        }
