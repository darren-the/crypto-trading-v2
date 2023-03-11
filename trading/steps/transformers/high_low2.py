from pipeline.task import Task
import numpy as np
from scipy.stats import spearmanr
from copy import deepcopy


class HighLow(Task):
    def __init__(self, symbol, timeframe, write_output=False, pivot=5):
        self.symbol = symbol
        self.timeframe = timeframe
        self.write_output = write_output
        self.pivot = pivot
        self.current_candles = []
        self.default = {
            'timestamp': -1,
            'top': -1,
            'bottom': -1,
        }
        self.current_high = deepcopy(self.default)
        self.current_low = deepcopy(self.default)
        self.next_high = deepcopy(self.default)
        self.next_low = deepcopy(self.default)
        self.alpha = 0
        super().__init__()

    def process(self, element):
        if len(self.current_candles) < self.pivot and element['is_complete']:
            self.current_candles.append(element)
        
        if self.alpha > 0:
            self._update_high(self.current_high, element)
        elif self.alpha < 0:
            self._update_low(self.current_low, element)

        high_low = {
            'timestamp': element['timestamp'],
            'is_high': False,
            'high_timestamp': self.current_high['timestamp'],
            'high_top': self.current_high['top'],
            'high_bottom': self.current_high['bottom'],
            'is_low': False,
            'low_timestamp': self.current_low['timestamp'],
            'low_top': self.current_low['top'],
            'low_bottom': self.current_low['bottom']
        }

        if len(self.current_candles) == self.pivot:
            new_alpha = self._calculate_alpha()
            if self.alpha == 0:
                self.alpha = new_alpha
            elif new_alpha != self.alpha:
                if new_alpha > 0:
                    high_low['is_low'] = True

                else:
                    high_low['is_high'] = True
                    
            self.current_candles.pop(0)


    
    def _calculate_alpha(self):
        base_alpha = spearmanr(np.arange(self.pivot), [candle['close'] for candle in self.current_candles])[0]
        return 1 if base_alpha >= 0 else -1
    
    def _update_high(self, high, element, min_timestamp=0, update_next=True):
        element_high_bottom = max(element['open'], element['close'])
        if high['timestamp'] < min_timestamp:
            # Initialise current high if it doesn't exist yet
            high['timestamp'] = element['timestamp']
            high['top'] = element['high']
            high['bottom'] = element_high_bottom
        else:
            # Update current high where possible
            if element['high'] > high['top']:
                high['timestamp'] = element['timestamp']
                high['top'] = element['high']
            if element_high_bottom > high['bottom']:
                high['bottom'] = element_high_bottom

        if update_next:
            self._update_low(self.next_low, element, high['timestamp'], False)
            self._update_high(self.next_high, element, self.next_low['timestamp'], False)
        
    def _update_low(self, low, element, min_timestamp=0, update_next=True):
        element_low_top = min(element['open'], element['close'])
        if low['timestamp'] < min_timestamp:
            # Initialise current low if it doesn't exist yet
            low['timestamp'] = element['timestamp']
            low['top'] = element_low_top
            low['bottom'] = element['low']
        else:
            # Update current low where possible
            if element['low'] < low['bottom']:
                low['timestamp'] = element['timestamp']
            if element_low_top < low['top']:
                low['top'] = element_low_top
        
        if update_next:
            self._update_high(self.next_high, element, low['timestamp'], False)
            self._update_low(self.next_low, element, self.next_high['timestamp'], False)