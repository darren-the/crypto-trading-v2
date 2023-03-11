from pipeline.task import Task


class Retracement(Task):
    def __init__(self, symbol: str, timeframe: str, write_output: bool=False):
        self.symbol = symbol
        self.timeframe = timeframe
        self.write_output = write_output
        self.prev_high = None
        self.prev_low = None
        self.is_high_first = None
        super().__init__()
    
    def process(self, element):
        retracement = {
            'timestamp': element['timestamp'],
            'high_retracement': -1,
            'low_retracement': -1,
        }

        if self.prev_high is not None and self.prev_low is not None:
            if element['high_top'] > 0:
                prev_low = self.prev_low if self.is_high_first else element['low_bottom']
                if self.prev_high == prev_low:
                    retracement['high_retracement'] = 0
                else:
                    retracement['high_retracement'] = round((element['high_top'] - prev_low) / (self.prev_high - prev_low), 3)
            if element['low_bottom'] > 0:
                prev_high = self.prev_high if not self.is_high_first else element['high_top']
                if prev_high == self.prev_low:
                    retracement['low_retracement'] = 0
                else:
                    retracement['low_retracement'] = round((prev_high - element['low_bottom']) / (prev_high - self.prev_low), 3)
        if element['is_high']:
            self.prev_high = element['high_top']
            self.is_high_first = False
        if element['is_low']:
            self.prev_low = element['low_bottom']
            self.is_high_first = True
        
        return retracement
    