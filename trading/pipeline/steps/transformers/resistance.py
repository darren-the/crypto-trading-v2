from pipeline.base_classes.task import Task
from copy import deepcopy


class Resistance(Task):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.default_res = {
            'is_res': False,
            'start_timestamp': -1,
            'end_timestamp': -1,
            'num_highs': 0,
            'top': -1,
            'bottom': -1,
            'top_history': '',
        }
        self.res_history = []
        super().__init__()

    def process(self, element):
        if element['is_high'] is False:
            res = deepcopy(self.default_res)
        
        else:
            # Clear any broken resistances
            while len(self.res_history) > 0 and self.res_history[-1]['top'] < element['high_bottom']:
                self.res_history.pop()

            new_res = {
                    'is_res': True,
                    'start_timestamp': element['high_timestamp'],
                    'end_timestamp': element['high_timestamp'],
                    'num_highs': 1,
                    'top': element['high_top'],
                    'bottom': element['high_bottom'],
                    'top_history': ''
                }
            # Add new resistance if there is no overlap with previous resistance
            if len(self.res_history) == 0 or self.res_history[-1]['bottom'] > element['high_top']:
                self.res_history.append(new_res)
            
            # Merge with previous resistances if there is overlap
            else:
                overlapping_res = []
                for i in range(len(self.res_history) -1, -1, -1):
                    if self.res_history[i]['top'] >= element['high_bottom'] \
                        and self.res_history[i]['bottom'] <= element['high_top']:
                        overlapping_res.insert(0, self.res_history[i])
                        self.res_history.pop()
                    else:
                        break
                overlapping_res.append(new_res)
                merged_res = {
                    'is_res': True,
                    'start_timestamp': min(item['start_timestamp'] for item in overlapping_res),
                    'end_timestamp': max(item['end_timestamp'] for item in overlapping_res),
                    'num_highs': sum(item['num_highs'] for item in overlapping_res),
                    'top': max(item['top'] for item in overlapping_res),
                    'bottom': max(item['bottom'] for item in overlapping_res),
                    'top_history': '',
                }
                self.res_history.append(merged_res)
                    
            res = deepcopy(self.res_history[-1])
        
        res['timestamp'] = element['timestamp']
        res['candle_timestamp'] = element['candle_timestamp']
        res['is_complete'] = element['is_complete']
        
        # Filter top history by num_highs
        filtered_res = []
        for i in range(len(self.res_history) - 1, -1, -1):
            if self.res_history[i]['num_highs'] >= 1:
                filtered_res = [self.res_history[i]['top']] + filtered_res
            if len(filtered_res) >= self.history_length:
                break
        res['top_history'] = ','.join([str(top) for top in filtered_res])

        return res
