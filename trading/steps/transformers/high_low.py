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
        self.high_low = {
            'timestamp': -1,
            'candle_timestamp': -1,
            'is_high': False,
            'high_timestamp': -1,
            'high_top': -1,
            'high_bottom': -1,
            'is_low': False,
            'low_timestamp': -1,
            'low_top': -1,
            'low_bottom': -1
        }
        self.alpha = 0
        super().__init__()

    def process(self, element):
        self.high_low['timestamp'] = element['timestamp']
        self.high_low['candle_timestamp'] = element['candle_timestamp']
        self.high_low['is_high'] = self.high_low['is_low'] = False

        if element['is_complete'] is True:
            self.current_candles.append(element)
            
            if len(self.current_candles) == self.pivot:  # 5
                self.alpha = self._calculate_alpha()

                if self.alpha > 0:  # currently searching for a high
                    self._reset_high(self.current_candles[0])
                    for candle in self.current_candles[1:]:
                        self._update_high(candle)

                else:  # currently searching for a low
                    self._reset_low(self.current_candles[0])
                    for candle in self.current_candles[1:]:
                        self._update_low(candle)

            elif len(self.current_candles) > self.pivot:
                self.current_candles.pop(0)  # Maintain current candles window at the pivot length
                self._update_high(element) if self.alpha > 0 else self._update_low(element)  # update current direction

                # check for direction change
                new_alpha = self._calculate_alpha()
                if new_alpha != self.alpha:  # a substantial direction change has occured
                    if new_alpha > 0:
                        self.high_low['is_low'] = True
                    else:
                        self.high_low['is_high'] = True
                    self.alpha = new_alpha
        
        return deepcopy(self.high_low)
    
    def _calculate_alpha(self):
        base_alpha = spearmanr(np.arange(self.pivot), [candle['close'] for candle in self.current_candles])[0]
        return 1 if base_alpha >= 0 else -1
    
    def _update_high(self, element, update_low=True):
        # Update high
        if element['high'] >= self.high_low['high_top']:
            self.high_low['high_top'] = element['high']
        bottom = max(element['open'], element['close'])
        if bottom >= self.high_low['high_bottom']:
            self.high_low['high_timestamp'] = element['candle_timestamp']
            self.high_low['high_bottom'] = bottom
        
        # Also update the low, limited to >= high_timestamp
        if update_low:
            if element['candle_timestamp'] > self.high_low['high_timestamp']:
                self._update_low(element, update_high=False)
            else:
                self._reset_low(element)
    
    def _update_low(self, element, update_high=True):
        # Update low
        if element['low'] <= self.high_low['low_bottom']:
            self.high_low['low_bottom'] = element['low']
        top = min(element['open'], element['close'])
        if top <= self.high_low['low_top']:
            self.high_low['low_timestamp'] = element['candle_timestamp']
            self.high_low['low_top'] = top
        
        if update_high:
            # Also update the high, limited to >= low_timestamp
            if element['candle_timestamp'] > self.high_low['low_timestamp']:
                self._update_high(element, update_low=False)
            else:
                self._reset_high(element)
    
    def _reset_high(self, element):
        self.high_low['high_timestamp'] = element['candle_timestamp']
        self.high_low['high_top'] = element['high']
        self.high_low['high_bottom'] = max(element['open'], element['close'])
    
    def _reset_low(self, element):
        self.high_low['low_timestamp'] = element['candle_timestamp']
        self.high_low['low_top'] = min(element['open'], element['close'])
        self.high_low['low_bottom'] = element['low']
