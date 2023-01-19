import apache_beam as beam
from utils.utils import timeframe_to_ms
from copy import deepcopy

class AggregateCandles(beam.DoFn):
    def __init__(self, timeframe: str):
        self.timeframe = timeframe
        self.start_timestamp = None
        self.base_ms = timeframe_to_ms('1m')
        self.ms = timeframe_to_ms(timeframe)
        self.last_candle = None
        self.rank = 0

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
            self.rank = 0
            self.last_candle = deepcopy(element)
            self.last_candle['rank'] = self.rank

        else:
            # Update candle
            self.rank += 1
            updated_candle = deepcopy(self.last_candle)
            updated_candle['close'] = element['close']
            updated_candle['rank'] = self.rank
            if updated_candle['high'] < element['high']:
                updated_candle['high'] = element['high']
            if updated_candle['low'] > element['low']:
                updated_candle['low'] = element['low']
            
            self.last_candle = updated_candle
        
        yield self.last_candle
