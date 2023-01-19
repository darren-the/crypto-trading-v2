import requests
import apache_beam as beam
import time
from datetime import datetime

# Testing a very basic pipeline with Apache Beam.
# 
# This script introduces the following Apache Beam concepts: batch processing, bounded sources, DoFn SDKs and ParDo transforms
# This also demonstrates a simple HTTP request to the Bitfinex API's Candle endpoint

# More information on things used in the code:
#   - Bitfinex candles endpoint: https://docs.bitfinex.com/reference/rest-public-candles
#   - ParDo function in Apache Beam: https://beam.apache.org/documentation/transforms/python/elementwise/pardo/#example-1-pardo-with-a-simple-dofn

def date_str_to_timestamp(date_str: str) -> int:
    """
    Args:
        date_str (str): A date string in the format YYYY-MM-DD
    
    Returns:
        int: a timestamp conversion of the given date string
    """
    return time.mktime(datetime.strptime(date_str, '%Y-%m-%d').timetuple()) * 1000


class FetchOCHL(beam.DoFn):
    """
    A DoFn class for fetching candlestick data from the bitfinex API.
    """
    
    def __init__(self):
        pass

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
                yield candle
        except:
            raise Exception('Invalid request.')
    
with beam.Pipeline() as p:
    OCHL = (
        p
        | beam.Create([0])
        | beam.ParDo(FetchOCHL())
        | beam.io.WriteToText('gs://crypto-trading-v2-dataflow/placeholder-pipeline-output', file_name_suffix='.txt')
    )
