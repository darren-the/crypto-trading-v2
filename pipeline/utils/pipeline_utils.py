import apache_beam as beam
from configs import config
from steps.candles.fetch_candles import FetchCandles
from utils.utils import date_str_to_timestamp
from math import ceil
import json
import time
import os

class IOHandler:
    def __init__(self, io_type='bigquery'):
        self.io_type = io_type

        # Calculate number of requests required for local pipeline run
        if io_type == 'text':
            num_reqs = ceil((date_str_to_timestamp(config.local_hist_end) - date_str_to_timestamp(config.local_hist_start))
                / 60_000 / config.bitfinex['candles']['max_data_per_req']) * len(config.symbols) * len(config.timeframes)
            current_time = time.time()
            new_req= {'timestamp': current_time, 'num_reqs': num_reqs}

            # Get the number of requests within the past minute
            past_reqs_filename = 'past_reqs.json'
            if os.path.exists(past_reqs_filename):
                with open(past_reqs_filename, 'r') as f:
                    past_reqs = json.load(f)
                    one_min_window_start = 0
                    num_past_reqs = 0
                    for i in range(len(past_reqs)):
                        if current_time - past_reqs[i]['timestamp'] > 60:
                            one_min_window_start = i + 1
                        else:
                            num_past_reqs += past_reqs[i]['num_reqs']
                    if num_past_reqs + num_reqs > config.bitfinex['candles']['max_req_per_min']:
                        raise Exception('The allowable number of requests has been exceeded. Try again later.')
                    
                    new_reqs = past_reqs[one_min_window_start:]
                    new_reqs.append(new_req)
            else:
                new_reqs = [new_req]

            # Store the new number of requests
            with open(past_reqs_filename, 'w') as f:
                json.dump(new_reqs, f)
    
    def symbols(self):
        for s in config.symbols:
            self.symbol = s
            yield s
    
    def timeframes(self):
        for t in config.timeframes:
            self.timeframe = t
            yield t

    def reader(self):
        read_label = f'{self.symbol}-{self.timeframe}-read'
        if self.io_type.lower() == 'bigquery':
            return read_label >> beam.io.ReadFromBigQuery(
                query=f'''
                    SELECT
                        timestamp
                        , open
                        , close
                        , high
                        , low
                    FROM [{self.symbol}.{config.table["basecandles"]}]
                    ORDER BY timestamp
                '''
            )
        else:
            return (
                f'{self.symbol}-{self.timeframe}-create' >> beam.Create([0])
                | read_label >> beam.ParDo(FetchCandles(config.local_hist_start, config.local_hist_end))
            )
            
    def writer(self, dofn):
        class Writer(beam.PTransform):
            def __init__(self, io_type, dofn, symbol, timeframe):
                self.io_type = io_type
                self.dofn = dofn
                self.config_name = str(type(dofn).__name__).lower()

                # labels
                self.dofn_label = f'{symbol}-{self.config_name}-{timeframe}'
                self.label = f'{symbol}-{self.config_name}-{timeframe}-writer'

                # write options
                self.table = f'{symbol}.{config.table[self.config_name]}-{timeframe}'
                self.schema = config.schema[self.config_name]
                self.writer = self._get_writer()

            def expand(self, pcoll):
                # Data will continue flowing through main branch
                main_branch = pcoll | self.dofn_label >> beam.ParDo(self.dofn)

                # create a separate branch to write data
                main_branch | self.writer  

                return main_branch

            def _get_writer(self):  
                if self.io_type.lower() == 'bigquery':
                    return f'{self.dofn_label}-bqwriter' >> beam.io.WriteToBigQuery(
                        table=self.table,    
                        schema={'fields': self.schema},
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                    )
                else:
                    return beam.io.WriteToText(f'./data/{self.table}', file_name_suffix='.txt')

        return Writer(self.io_type, dofn, self.symbol, self.timeframe)
