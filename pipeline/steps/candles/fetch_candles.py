import requests
import apache_beam as beam
from utils.utils import date_str_to_timestamp, timeframe_to_ms
from configs import config
import time


class FetchCandles(beam.DoFn):
    """
    A DoFn class for fetching candlestick data from the bitfinex API.
    """
    def __init__(self,  start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date

    def process(self, element):
        
        url = config.bitfinex['candles']['base_url']
        limit = config.bitfinex['candles']['max_data_per_req']
        interval = timeframe_to_ms('1m')
        start = date_str_to_timestamp(self.start_date)
        end = date_str_to_timestamp(self.end_date) - interval
        
        # Fetch candles in batches
        for i in range(start, end, limit * interval):
            batch_start = i
            batch_end = min(i + limit * interval, end)
            payload = {
                'start': batch_start,
                'end': batch_end,
                'sort': 1,
                'limit': limit,
            }

            try:
                candles = requests.get(url, params=payload).json()
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
            delay = (60 / config.bitfinex['candles']['max_req_per_min']) * len(config.symbols)
            time.sleep(delay)
