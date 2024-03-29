from pipeline.base_classes.task import Task
import numpy as np
from scipy.stats import spearmanr


class HighLow(Task):
    def __init__(self, *args, **kwargs):
        self.pivot = 5
        self.__dict__.update(kwargs)
        self.current_candles = []
        self.high_id = 0
        self.high_timestamp = -1
        self.high_top = -1
        self.high_bottom = -1
        self.high_colour = 'none'
        self.low_id = 0
        self.low_timestamp = -1
        self.low_top = -1
        self.low_bottom = -1
        self.low_colour = 'none'
        self.alpha = 0
        self.high_low = {}
        super().__init__()

    def process(self, element):
        self.high_low = {
            'timestamp': element['timestamp'],
            'candle_timestamp': element['candle_timestamp'],
            'is_high': False,
            'high_id': self.high_id,
            'high_timestamp': self.high_timestamp,
            'high_top': self.high_top,
            'high_bottom': self.high_bottom,
            'high_colour': self.high_colour,
            'is_low': False,
            'low_id': self.low_id,
            'low_timestamp': self.low_timestamp,
            'low_top': self.low_top,
            'low_bottom': self.low_bottom,
            'low_colour': self.low_colour,
            'is_complete': element['is_complete'],
        }
        
        # update current candles with new element
        if len(self.current_candles) == 0:
            self.current_candles.append(element)
        else:
            if self.current_candles[-1]['candle_timestamp'] == element['candle_timestamp']:
                self.current_candles[-1] = element
            else:
                self.current_candles.append(element)

        # update highs, lows and alpha
        if len(self.current_candles) >= self.pivot:
            if self.alpha == 0 and element['is_complete']:
                # initialise highs and lows
                self.alpha = self._calculate_alpha()

                if self.alpha > 0:  # currently searching for a high
                    self._init_high(self.current_candles[0])
                    for candle in self.current_candles[1:]:
                        self._update_high(candle)

                else:  # currently searching for a low
                    self._init_low(self.current_candles[0])
                    for candle in self.current_candles[1:]:
                        self._update_low(candle)

            if len(self.current_candles) > self.pivot:
                self.current_candles.pop(0)

            self._update_high(element) if self.alpha > 0 else self._update_low(element)

            if element['is_complete']:
                self._save_high_low()

                # check for direction change
                new_alpha = self._calculate_alpha()
                if new_alpha != self.alpha:  # a substantial direction change has occured
                    if new_alpha > 0:
                        self.high_low['is_low'] = True
                        self.low_id += 1
                        self._reset_low()
                    else:
                        self.high_low['is_high'] = True
                        self.high_id += 1
                        self._reset_high()
                    self.alpha = new_alpha

        return self.high_low
        
    def _calculate_alpha(self):
        base_alpha = spearmanr(np.arange(self.pivot), [candle['close'] for candle in self.current_candles])[0]
        return 1 if base_alpha >= 0 else -1

    def _update_high(self, element, update_low=True):
        if self.high_low['high_timestamp'] == -1:
            self._init_high(element)
        # Update high
        bottom = max(element['open'], element['close'])            
        if element['high'] > self.high_low['high_top']:
            self.high_low['high_timestamp'] = element['candle_timestamp']
            self.high_low['high_top'] = element['high']
            self._update_high_colour(element)
        if bottom > self.high_low['high_bottom']:
            self.high_low['high_bottom'] = bottom

        # Also update the low
        if update_low:
            if self.high_low['low_timestamp'] != -1:
                if self.high_low['high_timestamp'] > self.high_low['low_timestamp']:
                    self._reset_low(hard_reset=True)
                else:
                    self._update_low(element, False)
            if self.high_low['low_timestamp'] == -1 and element['open'] > element['close']:
                self._init_low(element)
    
    def _update_low(self, element, update_high=True):
        if self.high_low['low_timestamp'] == -1:
            self._init_low(element)
        # Update low
        top = min(element['open'], element['close'])
        if element['low'] < self.high_low['low_bottom']:
            self.high_low['low_timestamp'] = element['candle_timestamp']
            self.high_low['low_bottom'] = element['low']
            self._update_low_colour(element)
        if top < self.high_low['low_top']:
            self.high_low['low_top'] = top
        
        # Also update the high
        if update_high:
            if self.high_low['high_timestamp'] != -1:
                if self.high_low['low_timestamp'] > self.high_low['high_timestamp']:
                    self._reset_high(hard_reset=True)
                else:
                    self._update_high(element, False)
            if self.high_low['high_timestamp'] == -1 and element['open'] < element['close']:
                self._init_high(element)
    
    def _init_high(self, element):
        self.high_low['high_timestamp'] = element['candle_timestamp']
        self.high_low['high_top'] = element['high']
        self.high_low['high_bottom'] = max(element['open'], element['close'])
        self._update_high_colour(element)
    
    def _init_low(self, element):
        self.high_low['low_timestamp'] = element['candle_timestamp']
        self.high_low['low_top'] = min(element['open'], element['close'])
        self.high_low['low_bottom'] = element['low']
        self._update_low_colour(element)
    
    def _reset_high(self, hard_reset=False):
        self.high_timestamp = self.high_top = self.high_bottom = -1
        self.high_colour = 'none'
        if hard_reset:
            self.high_low['high_timestamp'] = self.high_low['high_top'] = self.high_low['high_bottom'] = -1
            self.high_low['high_colour'] = 'none'
    
    def _reset_low(self, hard_reset=False):
        self.low_timestamp = self.low_top = self.low_bottom = -1
        self.low_colour = 'none'
        if hard_reset:
            self.high_low['low_timestamp'] = self.high_low['low_top'] = self.high_low['low_bottom'] = -1
            self.high_low['low_colour'] = 'none'
    
    def _save_high_low(self):
        self.high_timestamp = self.high_low['high_timestamp']
        self.high_top = self.high_low['high_top']
        self.high_bottom = self.high_low['high_bottom']
        self.high_colour = self.high_low['high_colour']
        self.low_timestamp = self.high_low['low_timestamp']
        self.low_top = self.high_low['low_top']
        self.low_bottom = self.high_low['low_bottom']
        self.low_colour = self.high_low['low_colour']
    
    def _update_high_colour(self, element):
        if element['close'] > element['open']:
            self.high_low['high_colour'] = 'green'
        elif element['open'] > element['close']:
            self.high_low['high_colour'] = 'red'
        else:
            element['high_colour'] = 'none'
    
    def _update_low_colour(self, element):
        if element['close'] > element['open']:
            self.high_low['low_colour'] = 'green'
        elif element['open'] > element['close']:
            self.high_low['low_colour'] = 'red'
        else:
            element['low_colour'] = 'none'
