# Apache beam imports
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Imports for argument parsing
import argparse
from sys import argv

# Import pipeline utils and config variables
from pipeline.utils.pipeline_utils import PipelineWriter, PipelineWriterOptions
import pipeline.config as config

# Import candlestick steps
from pipeline.steps.candles.fetch_candles import FetchCandles
from pipeline.steps.candles.dedup_candles import DedupCandles
from pipeline.steps.candles.impute_candles import ImputeCandles
from pipeline.steps.candles.aggregate_candles import AggregateCandles

# Import transformers
from pipeline.steps.transformers import placeholder_transformer

def run():
    """TODO: Add description"""

    # Define beam options which are passed as command line arguments
    pipeline_keys = [
        'runner',
        'project',
        'job_name',
        'region',
        'temp_location',
        'setup_file',
    ]
    beam_parser = argparse.ArgumentParser()
    for key in pipeline_keys:
        beam_parser.add_argument(f'--{key}', dest=key)
    beam_args, other_argv = beam_parser.parse_known_args(argv[1:])
    beam_options = PipelineOptions(**vars(beam_args))

    # Define all other command line arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--start',
        dest='start',
        default=config.default_hist_start,
        help='Start date of historical data',
    )
    arg_parser.add_argument(
        '--end',
        dest='end',
        default=config.default_hist_end,
        help='End date of historical data',
    )
    arg_parser.add_argument(
        '--writer',
        dest='writer',
        default='TEXT',
        help='Write method of pipeline steps'
    )
    args = arg_parser.parse_args(other_argv)

    # Initialise pipeline step options
    writer_options = PipelineWriterOptions()
    writer_options.set_writer(args.writer)

    # Create and run the pipeline
    # If a step's output is to be written, wrap a PipelineWriter instance around it
    # These steps must have a defined table and schema in the pipeline config
    #
    # Otherwise, wrap it with a beam.ParDo instance
    with beam.Pipeline(options=beam_options) as p:
        setup_steps = p | beam.Create([0])
        
        # Symbol branching
        for s in config.symbols:
            writer_options.set_symbol(s)

            fetch_candles = (
                setup_steps
                | beam.ParDo(FetchCandles(args.start, args.end))  # TODO: if start and end gets passed frequently then may make it global
                | beam.ParDo(DedupCandles())
                | beam.ParDo(ImputeCandles(args.start, args.end))
            )
            
            # Timeframe branching
            for t in config.timeframes:
                writer_options.set_timeframe(t)

                (
                    fetch_candles | PipelineWriter(AggregateCandles(t))
                )
                

