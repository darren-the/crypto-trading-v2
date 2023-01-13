import requests
import apache_beam as beam
from pipeline.utils.utils import date_str_to_timestamp


class FetchCandles(beam.DoFn):
    """
    A DoFn class for fetching candlestick data from the bitfinex API.
    """

    def process(self, element):
        url = 'https://api-pub.bitfinex.com/v2/candles/trade:1m:tBTCUSD/hist'
        payload = {
            'start': date_str_to_timestamp('2022-01-01'),
            'end': date_str_to_timestamp('2022-01-02'),
            'sort': 1
        }
        try:
            candles = requests.get(url, params=payload).json()
            for candle in candles:
                yield {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'close': candle[2],
                    'high': candle[3],
                    'low': candle[4],
                }  # exclude volume for now
        except:
            raise Exception('Invalid request.')
