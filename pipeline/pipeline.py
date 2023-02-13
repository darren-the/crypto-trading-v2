# Apache beam imports
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Config variables and utils
from configs import config
from utils.pipeline_utils import Step

# Import candle steps
from steps.candles.fetch_candles import FetchCandles
from steps.candles.dedup_candles import DedupCandles
from steps.candles.impute_candles import ImputeCandles
from steps.candles.aggregate_candles import AggregateCandles

# Import transformers
from steps.transformers.HighLow import HighLow

# Other libraries
import argparse
import logging


def run():
    """TODO: Add description"""
    
    # Define custom command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--write_dest',
        default='text',
        help='Write destination of pipeline output e.g. text or bigquery',
    )
    args, beam_args = parser.parse_known_args()
    beam_options = PipelineOptions(beam_args, save_main_session=True)

    # Configure pipeline variables that depend on write destination
    if args.write_dest == 'text':
        logging.getLogger().setLevel(logging.INFO)  # add logger
        start_date = config.local_hist_start
        end_date = config.local_hist_end
    else:
        start_date = config.bq_hist_start
        end_date = config.bq_hist_end

    # Create and run the pipeline
    with beam.Pipeline(options=beam_options) as p:
        for symbol in config.symbols:
            for timeframe in config.timeframes:
                (
                    p | f'{symbol}-create-{timeframe}' >> beam.Create([0])

                    | Step(
                        step=FetchCandles(start_date, end_date, write_dest=args.write_dest),
                        symbol=symbol,
                        timeframe=timeframe,
                        write_dest=None)

                    | Step(
                        step=DedupCandles(),
                        symbol=symbol,
                        timeframe=timeframe,
                        write_dest=None)
                    
                    | Step(
                        step=ImputeCandles(start_date, end_date),
                        symbol=symbol,
                        timeframe=timeframe,
                        write_dest=None)

                    | Step(
                        step=AggregateCandles(timeframe)
                        , symbol=symbol
                        , timeframe=timeframe
                        , write_dest=args.write_dest)

                    | Step(
                        step=HighLow(pivot=5)
                        , symbol=symbol
                        , timeframe=timeframe
                        , write_dest=args.write_dest)   
                )
                

if __name__ == '__main__':
    run()
