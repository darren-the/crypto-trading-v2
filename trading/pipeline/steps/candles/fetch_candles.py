import requests
from pipeline.utils.utils import date_str_to_timestamp, timeframe_to_ms
from pipeline.configs import config
import time
from pipeline.base_classes.source import Source
from copy import deepcopy
import os


class FetchCandles(Source):
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.url = config.bitfinex['candle_url'][symbol]
        self.limit = config.bitfinex['max_data_per_req']
        self.interval = config.base_ms
        self.last_candle = None
        super().__init__()

    def generate(self):
        # Fetch candles in batches
        for i in range(self.start, self.end, self.limit * self.interval):
            batch_start = i
            batch_end = min(i + self.limit * self.interval, self.end - self.interval)
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

                # TODO: Minor enhancement: Check whether cancldes are missing between element and last WHEN we are at the final candle

                self.last_candle = element
                yield element

            # Calculate length of time delay to not breach req limit
            delay = 60 / config.bitfinex['max_req_per_min']
            time.sleep(delay)
        
        yield None
