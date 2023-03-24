from pipeline.base_classes.task import Task
from copy import deepcopy


class Support(Task):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.default_sup = {
            'is_sup': False,
            'start_timestamp': -1,
            'end_timestamp': -1,
            'num_lows': 0,
            'top': -1,
            'bottom': -1,
            'bottom_history': '',
        }
        self.sup_history = []
        super().__init__()

    def process(self, element):
        if element['is_low'] is False:
            sup = deepcopy(self.default_sup)
        
        else:
            # Clear any broken supports
            while len(self.sup_history) > 0 and self.sup_history[-1]['bottom'] > element['low_top']:
                self.sup_history.pop()

            # Create new support if there is no overlap with previous support
            if len(self.sup_history) == 0 or self.sup_history[-1]['top'] < element['low_bottom']:
                new_sup = {
                    'is_sup': True,
                    'start_timestamp': element['low_timestamp'],
                    'end_timestamp': element['low_timestamp'],
                    'num_lows': 1,
                    'top': element['low_top'],
                    'bottom': element['low_bottom'],
                    'bottom_history': ''
                }
                self.sup_history.append(new_sup)
            
            # Merge with previous support if there is overlap
            else:
                prev_sup = self.sup_history[-1]
                if prev_sup['bottom'] <= element['low_top'] and prev_sup['top'] >= element['low_bottom']:
                    prev_sup['end_timestamp'] = element['low_timestamp']
                    prev_sup['num_lows'] += 1
                    if prev_sup['bottom'] > element['low_bottom']:
                        prev_sup['bottom'] = element['low_bottom']
                    if prev_sup['top'] > element['low_top']:
                        prev_sup['top'] = element['low_top']
                    
            sup = deepcopy(self.sup_history[-1])
        
        sup['timestamp'] = element['timestamp']
        sup['candle_timestamp'] = element['candle_timestamp']
        sup['is_complete'] = element['is_complete']

        # Filter bottom history by num_lows
        filtered_sup = []
        for i in range(len(self.sup_history) - 1, -1, -1):
            if self.sup_history[i]['num_lows'] >= 2:
                filtered_sup = [self.sup_history[i]['bottom']] + filtered_sup
            if len(filtered_sup) >= self.history_length:
                break
        sup['bottom_history'] = ','.join([str(bottom) for bottom in filtered_sup])

        return sup
