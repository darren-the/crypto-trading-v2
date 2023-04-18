from pipeline.base_classes.timeframe_combiner import TimeframeCombiner
from pipeline.configs import config

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

        timeframes_from_retrace = []
        retracement_timeframe = 'no_timeframe'
        for i in range(len(self.reversed_timeframes)):
            # print(element, reversed_timeframes[i], flush=True)
            if 0.5 <= element[self.reversed_timeframes[i]]['high_retracement'] <= 1:
                retracement_timeframe = self.reversed_timeframes[i]
                timeframes_from_retrace = self.reversed_timeframes[i + 1:]
                break
        
        oversold_timeframe = 'no_timeframe'
        for t in timeframes_from_retrace:
            if self.oversold - self.oversold_offset <= element[t]['rsi'] <= self.oversold + self.oversold_offset:
                oversold_timeframe = t
                break
        
        # update long if conditions are met
        if retracement_timeframe != 'no_timeframe' and oversold_timeframe != 'no_timeframe':
            retracement_long = True

        return {
            'timestamp': element[config.base_timeframe]['timestamp'],
            'retracement_timeframe': retracement_timeframe,
            'high_retracement': -1 \
                if retracement_timeframe == 'no_timeframe' \
                else element[retracement_timeframe]['high_retracement'],
            'oversold_timeframe': oversold_timeframe,
            'retracement_long': retracement_long,
        }
        