from pipeline.base_classes.task import Task
from pipeline.utils.utils import timeframe_to_ms, date_str_to_timestamp
from copy import deepcopy
from pipeline.configs.config import weekly_start_date


class AggregateCandles(Task):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.start_timestamp = None
        self.weekly_start_timestamp = date_str_to_timestamp(weekly_start_date)
        self.base_ms = timeframe_to_ms('1m')
        self.ms = timeframe_to_ms(self.timeframe)
        self.last_candle = None
        super().__init__()

    def process(self, element):
        if self.start_timestamp is None:
            # start timestamp is currently used to determine when all candle start and end
            # (by measuring the difference between a new candle's timestamp and the start timestamp)
            # This could become problematic if for e.g. a timeframe is 1 month but the start timestamp
            # is in the middle of the month.
            # TODO: Fix above bug once newer timeframes are introduced
            # EDIT: this has been accomplished for the weekly timeframe. The monthly aggregation is another beast entirely.

            self.start_timestamp = element['timestamp']

            if self.timeframe[-1] == 'W':
                # initialise candle for when the start_timestamp isn't at the start of the candle
                self.last_candle = deepcopy(element)
                # round down to the nearest timeframe interval
                self.last_candle['candle_timestamp'] = element['timestamp'] \
                    - ((element['timestamp'] - self.weekly_start_timestamp) % self.ms)
                if (element['timestamp'] - self.weekly_start_timestamp + self.base_ms) % self.ms == 0:
                    self.last_candle['is_complete'] = True
                else:
                    self.last_candle['is_complete'] = False

        # Refresh last candles
        if (self.timeframe[-1] == 'W' and (element['timestamp'] - self.weekly_start_timestamp) % self.ms == 0) \
            or (self.timeframe[-1] != 'W' and (element['timestamp'] - self.start_timestamp) % self.ms == 0):
            self.last_candle = deepcopy(element)
            self.last_candle['candle_timestamp'] = element['timestamp']
            self.last_candle['is_complete'] = False if self.ms > self.base_ms else True

        else:
            # Update candle
            updated_candle = deepcopy(self.last_candle)
            updated_candle['close'] = element['close']
            updated_candle['timestamp'] = element['timestamp']

            if (self.timeframe[-1] == 'W' and (element['timestamp'] - self.weekly_start_timestamp + self.base_ms) % self.ms == 0) \
                or (self.timeframe[-1] != 'W' and (element['timestamp'] - self.start_timestamp + self.base_ms) % self.ms == 0):
                updated_candle['is_complete'] = True

            if updated_candle['high'] < element['high']:
                updated_candle['high'] = element['high']
            if updated_candle['low'] > element['low']:
                updated_candle['low'] = element['low']
            
            self.last_candle = updated_candle
        
        return self.last_candle
