# Apache beam imports
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Argument parsing
import argparse

# Config variables
from configs import config

# Import candlestick steps
from steps.candles.fetch_candles import FetchCandles
from steps.candles.dedup_candles import DedupCandles
from steps.candles.impute_candles import ImputeCandles


def run():
    """TODO: Add description"""

    # Define beam options which are passed as command line arguments
    parser = argparse.ArgumentParser()
    args, beam_args = parser.parse_known_args()
    beam_options = PipelineOptions(beam_args, save_main_session=True)

    # Create and run the pipeline
    with beam.Pipeline(options=beam_options) as p:
        
        # Symbol branching
        for s in config.symbols:
            (
                p 
                | beam.Create([0]) 
                | beam.ParDo(FetchCandles(config.bq_hist_start, config.bq_hist_end))
                | beam.ParDo(DedupCandles())
                | beam.ParDo(ImputeCandles(config.default_hist_start, config.default_hist_end))
                | beam.io.WriteToBigQuery(
                    table=f'{s}.{config.table["basecandles"]}',
                    schema={'fields': config.schema["basecandles"]},
                    write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                )
            )

if __name__ == '__main__':
    run()
