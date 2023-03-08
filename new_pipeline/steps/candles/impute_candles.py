import apache_beam as beam
from utils.utils import date_str_to_timestamp, timeframe_to_ms
from copy import deepcopy


# TODO: Fix bug where missing candles between the last available candle and the specified end date
# are unable to be imputed given the current logic.

class ImputeCandles(beam.DoFn):
    """
    A DoFn class for imputing missing candlestick data.
    """

    def __init__(self,  start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date
        self.start_timestamp = date_str_to_timestamp(start_date)
        self.end_timestamp = date_str_to_timestamp(end_date)
        self.last_candle = None
        self.interval = timeframe_to_ms('1m')
    
    def process(self, element):
        if element['timestamp'] < self.start_timestamp or element['timestamp'] >= self.end_timestamp:
            raise Exception(f'{element["timestamp"]} is a timestamp outside the start and end range')

        # Check whether the first candles are missing
        if self.last_candle is None and element['timestamp'] != self.start_timestamp:
            # Copy the OCHL data from the next most available candle
            for t in range(self.start_timestamp, element['timestamp'], self.interval):
                element_copy = deepcopy(element)
                element_copy['timestamp'] = t
                yield element_copy

        # Check whether other candles are missing
        elif self.last_candle is not None and element['timestamp'] - self.last_candle['timestamp'] > self.interval:
            # Copy the OCHL data from the last available candle
            for t in range(self.last_candle['timestamp'] + self.interval, element['timestamp'], self.interval):
                last_copy = deepcopy(self.last_candle)
                last_copy['timestamp'] = t
                yield last_copy

        self.last_candle = element
        yield element
