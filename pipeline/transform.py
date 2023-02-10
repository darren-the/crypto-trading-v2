# Apache beam imports
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Config variables and utils
from configs import config
from utils.pipeline_utils import IOHandler

# Import steps
from steps.candles.aggregate_candles import AggregateCandles
from steps.transformers import placeholder_transformer

# Other libraries
import argparse
import logging

def run():
    """TODO: Add description"""
    
    # Define custom command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--io_type',
        default='text',
        help='Input/output type of the pipeline',
    )
    args, beam_args = parser.parse_known_args()
    beam_options = PipelineOptions(beam_args, save_main_session=True)

    # Input/output handler
    io = IOHandler(args.io_type)
    if args.io_type == 'text':
        logging.getLogger().setLevel(logging.INFO)  # add logger 

    # Create and run the pipeline
    with beam.Pipeline(options=beam_options) as p:
        
        # Symbol branching
        for s in io.symbols():

            # Timeframe branching
            for t in io.timeframes():
                (
                    p 
                    | io.reader()
                    | io.writer(AggregateCandles(t))
                )
                

if __name__ == '__main__':
    run()
