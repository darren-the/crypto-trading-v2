import requests
import apache_beam as beam
from utils.utils import date_str_to_timestamp, timeframe_to_ms
from configs import config
from math import ceil
import time


class FetchCandles(beam.DoFn):
    """
    A DoFn class for fetching candlestick data from the bitfinex API.
    """
    def __init__(self,  start_date: str, end_date: str, write_dest: str):
        self.url = config.bitfinex['candles']['base_url']
        self.limit = config.bitfinex['candles']['max_data_per_req']
        self.interval = timeframe_to_ms('1m')
        self.start = date_str_to_timestamp(start_date)
        self.end = date_str_to_timestamp(end_date) - self.interval
        self.write_dest = write_dest

    def process(self, element):
        
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
                yield {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'close': candle[2],
                    'high': candle[3],
                    'low': candle[4],
                    # exclude volume for now
                }
            
            # Calculate length of time delay to not breach req limit
            delay = self._get_delay()
            time.sleep(delay)

    def _get_delay(self):
        if self.write_dest == 'bigquery':
            return (60 / self.limit)
        else:
            num_reqs = ceil((self.end - self.start)
                / self.interval / self.limit) * len(config.symbols) * len(config.timeframes)
            
            if num_reqs <= self.limit:
                return 0
            
            else:
                return (60 / self.limit) * len(config.symbols) * len(config.timeframes)