import requests
from utils.utils import date_str_to_timestamp, timeframe_to_ms
from configs import config
from math import ceil
import time
from pipeline.source import Source
from copy import deepcopy


class FetchCandles(Source):
    """
    A DoFn class for fetching candlestick data from the bitfinex API.
    """
    def __init__(self,  start_date: str, end_date: str):
        self.url = config.bitfinex['candles']['base_url']
        self.limit = config.bitfinex['candles']['max_data_per_req']
        self.interval = timeframe_to_ms('1m')
        self.start = date_str_to_timestamp(start_date)
        self.end = date_str_to_timestamp(end_date) - self.interval
        self.last_candle = None
        super().__init__()

    def generate(self):
        # Fetch candles in batches
        for i in range(self.start, self.end, self.limit * self.interval):
            batch_start = i
            batch_end = min(i + self.limit * self.interval, self.end)
            payload = {
                'start': batch_start,
                'end': batch_end,
                'sort': 1,
                'limit': self.limit,
            }

            try:
                candles = requests.get(self.url, params=payload).json()
            except:
                raise Exception('Invalid request.')

            for candle in candles:
                element = {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'close': candle[2],
                    'high': candle[3],
                    'low': candle[4],
                }

                # Skip duplicates
                if self.last_candle is not None and self.last_candle['timestamp'] == element['timestamp']:
                    continue

                # Check whether the first candles are missing
                if self.last_candle is None and element['timestamp'] != self.start:
                    # Copy the OCHL data from the next most available candle
                    for t in range(self.start, element['timestamp'], self.interval):
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

            # Calculate length of time delay to not breach req limit
            delay = self._get_delay()
            time.sleep(delay)
        
        yield None

    def _get_delay(self):
        num_reqs = ceil((self.end - self.start)
            / self.interval / self.limit) * len(config.symbols) * len(config.timeframes)
        
        if num_reqs <= self.limit:
            return 0
        
        else:
            return (60 / self.limit) * len(config.symbols) * len(config.timeframes)