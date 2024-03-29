from pipeline.base_classes.task import Task
from pipeline.utils.parsers import parse_high_low_history


class Retracement(Task):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.prev_high = None
        self.prev_low = None
        super().__init__()
    
    def process(self, element):
        retracement = {
            'timestamp': element['timestamp'],
            'candle_timestamp': element['candle_timestamp'],
            'high_retracement': 0,
            'high_retracement_high': -1,
            'high_retracement_low': -1,
            'low_retracement': 0,
            'low_retracement_high': -1,
            'low_retracement_low': -1,
            'is_complete': element['is_complete'],
        }

        high_low_history = parse_high_low_history(element)

        # Store the last two high/lows necessary for retracement calculation
        last_high_then_low = []
        last_low_then_high = []
        while len(high_low_history) > 0:
            hl = high_low_history.pop()
            if hl['type'] == 'high':
                if len(last_low_then_high) == 0:
                    last_low_then_high.insert(0, hl)
                elif len(last_low_then_high) == 1:
                    last_low_then_high[0] = hl
                if len(last_high_then_low) == 1 and hl['confirmed']:
                    last_high_then_low.insert(0, hl)
            else:
                if len(last_high_then_low) == 0:
                    last_high_then_low.insert(0, hl)
                elif len(last_high_then_low) == 1:
                    last_high_then_low[0] = hl
                if len(last_low_then_high) == 1 and hl['confirmed']:
                    last_low_then_high.insert(0, hl)
            if len(last_high_then_low) == 2 and len(last_low_then_high) == 2:
                break

        # Calculate low retracement
        if len(last_high_then_low) == 2:
            high = last_high_then_low[0]
            low = last_high_then_low[1]
            denom = high['price'] - low['price']
            if denom > 0:
                retracement['low_retracement'] = (element['close'] - low['price']) / denom
                retracement['low_retracement_high'] = high['price']
                retracement['low_retracement_low'] = low['price']

        # Calculate high retracement
        if len(last_low_then_high) == 2:
            low = last_low_then_high[0]
            high = last_low_then_high[1]
            denom = high['price'] - low['price']
            if denom > 0:
                retracement['high_retracement'] = (high['price'] - element['close']) / denom
                retracement['high_retracement_high'] = high['price']
                retracement['high_retracement_low'] = low['price']
    
        return retracement
    