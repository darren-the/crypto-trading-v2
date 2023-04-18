from pipeline.base_classes.timeframe_combiner import TimeframeCombiner
from pipeline.configs import config

class RetracementLong(TimeframeCombiner):
    def __init__(self, *args, **kwargs):
        self.oversold = 30
        self.oversold_offset = 2.5
        self.__dict__.update(kwargs)
        super().__init__()
    
    def process(self, element):
        # Identify timeframes to process based on retracement
        reversed_timeframes = list(reversed(config.timeframes))
        timeframes_from_retrace = []
        retracement_timeframe = 'no_timeframe'
        for i in range(len(reversed_timeframes)):
            # print(element, reversed_timeframes[i], flush=True)
            if 0.5 <= element[reversed_timeframes[i]]['high_retracement'] <= 1:
                timeframes_from_retrace = reversed_timeframes[i:]
                break
        
        oversold_timeframe = 'no_timeframe'
        for t in timeframes_from_retrace:
            if self.oversold - self.oversold_offset <= element[t]['rsi'] <= self.oversold + self.oversold_offset:
                oversold_timeframe = t
                break
      
        return {
            'timestamp': element[config.base_timeframe]['timestamp'],
            'retracement_timeframe': retracement_timeframe,
            'high_retracement': -1 \
                if retracement_timeframe == 'no_timeframe' \
                else element[retracement_timeframe]['high_retracement'],
            'oversold_timeframe': oversold_timeframe,
            'retracement_long': False if oversold_timeframe == 'no_timeframe' else True,
        }
        