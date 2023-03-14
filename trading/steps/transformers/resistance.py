from pipeline.task import Task
from copy import deepcopy


class Resistance(Task):
    def __init__(self, symbol, timeframe, write_output=False, history_length=10):
        self.symbol = symbol
        self.timeframe = timeframe
        self.write_output = write_output
        self.default_res = {
            'is_res': False,
            'start_timestamp': -1,
            'end_timestamp': -1,
            'num_highs': 0,
            'top': -1,
            'bottom': -1,
            'top_history': ''
        }
        self.res_history = []
        self.history_length = history_length
        super().__init__()

    def process(self, element):
        if element['is_high'] is False:
            res = deepcopy(self.default_res)
        
        else:
            # Clear any broken resistances
            while len(self.res_history) > 0 and self.res_history[-1]['top'] < element['high_bottom']:
                self.res_history.pop()

            # Create new resistance if there is no overlap with previous resistance
            if len(self.res_history) == 0 or self.res_history[-1]['bottom'] > element['high_top']:
                new_res = {
                    'is_res': True,
                    'start_timestamp': element['high_timestamp'],
                    'end_timestamp': element['high_timestamp'],
                    'num_highs': 1,
                    'top': element['high_top'],
                    'bottom': element['high_bottom'],
                    'top_history': ''
                }
                self.res_history.append(new_res)
            
            # Merge with previous resistance if there is overlap
            else:
                prev_res = self.res_history[-1]
                if prev_res['top'] >= element['high_bottom'] and prev_res['bottom'] <= element['high_top']:
                    prev_res['end_timestamp'] = element['high_timestamp']
                    prev_res['num_highs'] += 1
                    if prev_res['top'] < element['high_top']:
                        prev_res['top'] = element['high_top']
                    if prev_res['bottom'] < element['high_bottom']:
                        prev_res['bottom'] = element['high_bottom']
                    
            res = deepcopy(self.res_history[-1])
        
        res['timestamp'] = element['timestamp']
        res['candle_timestamp'] = element['candle_timestamp']
        
        # Filter top history by num_highs
        filtered_res = []
        for i in range(len(self.res_history) - 1, -1, -1):
            if self.res_history[i]['num_highs'] >= 2:
                filtered_res = [self.res_history[i]['top']] + filtered_res
            if len(filtered_res) >= self.history_length:
                break
        res['top_history'] = ','.join([str(top) for top in filtered_res])

        return res
