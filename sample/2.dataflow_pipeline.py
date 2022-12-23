import requests
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Testing a very basic pipeline in dataflow.

# Inspirations:
# https://cloud.google.com/dataflow/docs/guides/setting-pipeline-options#python_2
# https://medium.com/@aishwarya.gupta3/cloud-function-to-start-a-data-flow-job-on-a-new-file-upload-in-google-cloud-storage-using-trigger-30270b31a06d
# https://beam.apache.org/documentation/sdks/python-pipeline-dependencies/


class FetchOCHL(beam.DoFn):
    def __init__(self):
        pass

    def process(self, element):
        url = 'https://api-pub.bitfinex.com/v2/candles/trade:1m:tBTCUSD/hist'
        payload = {
            'start': 1640955600000,
            'end': 1641042000000,
            'sort': 1
        }
        try:
            candles = requests.get(url, params=payload).json()
            for candle in candles:
                yield candle
        except:
            raise Exception('Invalid request.')

beam_options = PipelineOptions(
    runner='DataflowRunner',
    project='crypto-trading-v2',
    job_name='hist-pipeline',
    region='us-central1',
    temp_location='gs://dataflow-apache-quickstart_crypto-trading-v2'
)

with beam.Pipeline(options=beam_options) as p:
    OCHL = (
        p
        | beam.Create([0])
        | beam.ParDo(FetchOCHL())
        | beam.io.WriteToText('gs://dataflow-apache-quickstart_crypto-trading-v2/dataflow-output', file_name_suffix='.txt')
    )
