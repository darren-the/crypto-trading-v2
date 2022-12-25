import apache_beam as beam
import argparse
from sys import argv
from apache_beam.options.pipeline_options import PipelineOptions
from pipeline.steps.fetch_candles import FetchCandles


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
    pipeline_args, other_argv = pipeline_parser.parse_known_args(argv[1:])
    pipeline_options = PipelineOptions(**vars(pipeline_args))

    # Define all other command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output',
        dest='output',
        default='local_test_data',
        help='Output file to write results to.',
    )
    args = parser.parse_args(other_argv)

    # Run pipeline steps
    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | beam.Create([0])
            | beam.ParDo(FetchCandles())
            | beam.io.WriteToText(args.output, file_name_suffix='.txt')
        )
    