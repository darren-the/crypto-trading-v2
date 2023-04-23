from pipeline.base_classes.timeframe_combiner import TimeframeCombiner
from pipeline.configs import config
from pipeline.utils.utils import timeframe_to_ms, timestamp_to_date
from copy import copy

CREATE = 0
CLEAR = 1
MERGE = 2

class SupportCombiner(TimeframeCombiner):
    def __init__(self, *args, **kwargs):
        self.ignore_timeframes = []
        self.__dict__.update(kwargs)
        self.timeframes = copy(config.timeframes)
        for t in self.ignore_timeframes:
            self.timeframes.remove(t)
        self.sup_history = []
        self.sup_id = -1
        self.extra_output_names = ['support_history_log']
        super().__init__()
    
    def process(self, element):
        support_history_log = []
        for t in self.timeframes:
            if element[t]['is_low']:
                # Clear any broken supports
                i = len(self.sup_history) - 1

                while i >= 0 and self.sup_history[i]['sup_bottom'] > element[t]['low_top']:
                    if timeframe_to_ms(self.sup_history[i]['max_timeframe']) <= timeframe_to_ms(t):
                        # mark as cleared support
                        cleared_sup = copy(self.sup_history.pop(i))
                        cleared_sup['timestamp'] = element[t]['timestamp']
                        cleared_sup['time'] = timestamp_to_date(element[t]['timestamp'] / 1000)
                        cleared_sup['last_update'] = CLEAR
                        support_history_log.append(cleared_sup)
                    i -= 1
                
                new_sup = self._create_sup(element, t)
                if len(self.sup_history) == 0 or self.sup_history[-1]['sup_top'] < element[t]['low_bottom']:
                    # Add new support if there is no overlap with previous support
                    self._insert_sup(new_sup)
                    support_history_log.append(new_sup)
                else:
                    # Merge with previous supports if there is overlap
                    overlapping_sups = []
                    for i in range(len(self.sup_history) -1, -1, -1):
                        if self.sup_history[i]['sup_bottom'] <= new_sup['sup_top'] \
                            and self.sup_history[i]['sup_top'] >= new_sup['sup_bottom']:  
                            overlapping_sups.insert(0, self.sup_history[i])
                            # mark as merged support
                            merged_sup = copy(self.sup_history.pop(i))
                            merged_sup['timestamp'] = element[t]['timestamp']
                            merged_sup['time'] = timestamp_to_date(element[t]['timestamp'] / 1000)
                            merged_sup['last_update'] = MERGE
                            support_history_log.append(merged_sup)
                        else:
                            break
                    overlapping_sups.append(new_sup)
                    merged_max_timeframe = max(
                        [item['max_timeframe'] for item in overlapping_sups],
                        key=lambda x: timeframe_to_ms(x)
                    )
                    # determine merged top value
                    merged_top = -1
                    for sup in overlapping_sups:
                        if sup['max_timeframe'] == merged_max_timeframe:
                            merged_top = sup['sup_top'] if merged_top == -1 else min(merged_top, sup['sup_top'])

                    new_sup['max_timeframe'] = merged_max_timeframe
                    new_sup['start_timestamp'] = min(item['start_timestamp'] for item in overlapping_sups)
                    new_sup['end_timestamp'] = max(item['end_timestamp'] for item in overlapping_sups)
                    new_sup['sup_factor'] = sum(item['sup_factor'] for item in overlapping_sups)
                    new_sup['sup_top'] = merged_top
                    new_sup['sup_bottom'] = min(item['sup_bottom'] for item in overlapping_sups)
                    
                    self._insert_sup(new_sup)
                    support_history_log.append(new_sup)

        return {
            'timestamp': element[config.base_timeframe]['timestamp'],
            'candle_timestamp': element[config.base_timeframe]['candle_timestamp'],
            # 'support': '[]',
            'support_history_log': support_history_log,
            'is_complete': element[config.base_timeframe]['is_complete'],
        }

    def _create_sup(self, element, t):
        self.sup_id += 1
        return {
            'timestamp': element[t]['timestamp'],
            'time': timestamp_to_date(element[t]['timestamp'] / 1000),
            'sup_id': self.sup_id,
            'last_update': CREATE,
            'max_timeframe': t,
            'start_timestamp': element[t]['low_timestamp'],
            'end_timestamp': element[t]['low_timestamp'],
            'sup_factor': timeframe_to_ms(t),
            'sup_top': element[t]['low_top'],
            'sup_bottom': element[t]['low_bottom'],
        }
    
    def _insert_sup(self, sup):
        i = len(self.sup_history) - 1
        while i >= 0 and self.sup_history[i]['sup_bottom'] > sup['sup_bottom']:
            i -= 1
        i += 1
        self.sup_history.insert(i, sup)