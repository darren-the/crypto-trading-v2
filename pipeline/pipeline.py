import apache_beam as beam
import argparse
from sys import argv
from apache_beam.options.pipeline_options import PipelineOptions
from pipeline.steps.fetch_candles import FetchCandles
from pipeline.utils.pipeline_utils import PipelineStep, pipeline_step_options
import pipeline.config as config


def run():
    """TODO: Add description"""

    # Define pipeline options which are passed as command line arguments
    pipeline_keys = [
        'runner',
        'project',
        'job_name',
        'region',
        'temp_location',
        'setup_file',
    ]
    pipeline_parser = argparse.ArgumentParser()
    for key in pipeline_keys:
        pipeline_parser.add_argument(f'--{key}', dest=key)
    pipeline_args, _ = pipeline_parser.parse_known_args(argv[1:])
    pipeline_options = PipelineOptions(**vars(pipeline_args))

    # Configure write destination of pipeline steps
    if pipeline_args.runner == 'DataflowRunner':
        pipeline_step_options['writer'] = 'BIGQUERY'

    # Create and run pipeline
    with beam.Pipeline(options=pipeline_options) as p:
        setup_steps = p | beam.Create([0])
        
        # Symbol branching
        for symbol in config.symbols:
            
            # Timeframe branching
            for timeframe in config.timeframes:
                pipeline_step_options['symbol'] = symbol
                pipeline_step_options['timeframe'] = timeframe

                setup_steps | PipelineStep(FetchCandles())
