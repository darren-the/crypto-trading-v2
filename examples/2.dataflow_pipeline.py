import requests
import apache_beam as beam
import time
from datetime import datetime
import argparse
from apache_beam.pipeline import PipelineOptions


class FetchOCHL(beam.DoFn):
    """
    A DoFn class for fetching candlestick data from the bitfinex API.
    """
    
    def __init__(self):
        pass

    def process(self, element):
        url = 'https://api-pub.bitfinex.com/v2/candles/trade:1m:tBTCUSD/hist'
        payload = {
            'start': self.date_str_to_timestamp('2022-01-01'),
            'end': self.date_str_to_timestamp('2022-01-02'),
            'sort': 1
        }
        try:
            candles = requests.get(url, params=payload).json()
            for candle in candles:
                yield candle
        except:
            raise Exception('Invalid request.')
    
    def date_str_to_timestamp(self, date_str: str) -> int:
        """
        Args:
            date_str (str): A date string in the format YYYY-MM-DD
        
        Returns:
            int: a timestamp conversion of the given date string
        """
        return time.mktime(datetime.strptime(date_str, '%Y-%m-%d').timetuple()) * 1000

parser = argparse.ArgumentParser()

_, beam_args = parser.parse_known_args()
options = PipelineOptions(beam_args, save_main_session=True)

with beam.Pipeline(options=options) as p:
    OCHL = (
        p
        | beam.Create([0])
        | beam.ParDo(FetchOCHL())
        | beam.io.WriteToText('gs://crypto-trading-v2-dataflow/placeholder-pipeline-output', file_name_suffix='.txt')
    )
