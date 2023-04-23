from pipeline.base_classes.timeframe_combiner import TimeframeCombiner
from pipeline.configs import config
import json

class RetracementLong(TimeframeCombiner):
    def __init__(self, *args, **kwargs):
        self.oversold = 30
        self.oversold_offset = 2.5
        self.ignore_timeframes = []
        self.__dict__.update(kwargs)

        # Identify timeframes to process based on retracement
        self.reversed_timeframes = list(reversed(config.timeframes))
        for t in self.ignore_timeframes:
            self.reversed_timeframes.remove(t)

        super().__init__()
    
    def process(self, element):
        retracement_long = False

        # check retracement
        timeframes_from_retrace = []
        retracement_timeframe = 'no_timeframe'
        for i in range(len(self.reversed_timeframes)):
            # print(element, reversed_timeframes[i], flush=True)
            if 0.5 <= element[self.reversed_timeframes[i]]['high_retracement'] <= 1:
                retracement_timeframe = self.reversed_timeframes[i]
                timeframes_from_retrace = self.reversed_timeframes[i + 1:]
                break
        
        # check rsi
        oversold_timeframe = 'no_timeframe'
        for t in timeframes_from_retrace:
            if self.oversold - self.oversold_offset <= element[t]['rsi'] <= self.oversold + self.oversold_offset:
                oversold_timeframe = t
                break

        # update long if conditions are met
        support_range = [-1, -1]
        if retracement_timeframe != 'no_timeframe' \
            and oversold_timeframe != 'no_timeframe' \
            and element[oversold_timeframe]['avg_rsi'] > self.oversold:
            retracement_long = True
            support_range = [element[retracement_timeframe]['high_retracement_low'], element[config.base_timeframe]['close']]
        
        return {
            'timestamp': element[config.base_timeframe]['timestamp'],
            'retracement_timeframe': retracement_timeframe,
            'high_retracement': -1 \
                if retracement_timeframe == 'no_timeframe' \
                else element[retracement_timeframe]['high_retracement'],
            'oversold_timeframe': oversold_timeframe,
            'avg_rsi': -1 \
                if oversold_timeframe == 'no_timeframe' \
                else element[oversold_timeframe]['avg_rsi'],
            'support_range': json.dumps(support_range),
            'retracement_long': retracement_long,
        }
        