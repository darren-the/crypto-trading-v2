# Apache beam imports
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Argument parsing
import argparse

# Config variables
from configs import config

# Import steps
from steps.candles.aggregate_candles import AggregateCandles
from steps.transformers import placeholder_transformer


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

            # Timeframe branching
            for t in config.timeframes:
                (
                    p 
                    | f'{s}-{t}-read' >> beam.io.ReadFromBigQuery(
                        query=f'''
                            SELECT
                                timestamp
                                , open
                                , close
                                , high
                                , low
                            FROM [{s}.{config.table["basecandles"]}]
                            ORDER BY timestamp
                        '''
                    ) 
                    | f'{s}-{t}-aggregate' >> beam.ParDo(AggregateCandles(t))
                    | f'{s}-{t}-write' >> beam.io.WriteToBigQuery(
                        table=f'{s}.{config.table["aggregatecandles"]}-{t}',
                        schema={'fields': config.schema["aggregatecandles"]},
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                    )
                )
                

if __name__ == '__main__':
    run()
