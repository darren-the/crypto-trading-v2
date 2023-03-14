from pipeline.task import Task
from utils.utils import timeframe_to_ms
from copy import deepcopy

class AggregateCandles(Task):
    def __init__(self, symbol: str, timeframe: str, write_output=False):
        self.symbol = symbol
        self.timeframe = timeframe
        self.start_timestamp = None
        self.base_ms = timeframe_to_ms('1m')
        self.ms = timeframe_to_ms(timeframe)
        self.last_candle = None
        self.write_output = write_output
        super().__init__()

    def process(self, element):
        if self.start_timestamp is None:
            # start timestamp is currently used to determine when all candle start and end
            # (by measuring the difference between a new candle's timestamp and the start timestamp)
            # This could become problematic if for e.g. a timeframe is 1 month but the start timestamp
            # is in the middle of the month.
            # TODO: Fix above bug once newer timeframes are introduced

            self.start_timestamp = element['timestamp']

        # Refresh last candles
        if (element['timestamp'] - self.start_timestamp) % self.ms == 0:
            self.last_candle = deepcopy(element)
            self.last_candle['candle_timestamp'] = element['timestamp']
            self.last_candle['is_complete'] = False if self.ms > self.base_ms else True

        else:
            # Update candle
            updated_candle = deepcopy(self.last_candle)
            updated_candle['close'] = element['close']
            updated_candle['timestamp'] = element['timestamp']

            if (element['timestamp'] - self.start_timestamp + self.base_ms) % self.ms == 0:
                updated_candle['is_complete'] = True

            if updated_candle['high'] < element['high']:
                updated_candle['high'] = element['high']
            if updated_candle['low'] > element['low']:
                updated_candle['low'] = element['low']
            
            self.last_candle = updated_candle
        
        return self.last_candle
