import apache_beam as beam
from configs import config


class Step(beam.PTransform):
    def __init__(self, step, symbol, timeframe, write_dest=None):
        self.step = step
        self.write_dest = write_dest
        step_name = str(type(step).__name__).lower()

        # labels
        self.label = f'{symbol}-{step_name}-{timeframe}-step'
        self.step_label = f'{symbol}-{step_name}-{timeframe}'
        
        # write options
        if self.write_dest is not None:
            self.table = f'{symbol}.{config.table[step_name]}-{timeframe}'
            self.schema = config.schema[step_name]
            self.writer = self._get_writer()

    def expand(self, pcoll):
        # Data will continue flowing through main branch
        main_branch = pcoll | self.step_label >> beam.ParDo(self.step)

        # create a separate branch to write data
        if self.write_dest is not None:
            main_branch | self.writer

        return main_branch

    def _get_writer(self):
        if self.write_dest.lower() == 'bigquery':
            writer = beam.io.WriteToBigQuery(
                table=self.table,    
                schema={'fields': self.schema},
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        else:
            writer = beam.io.WriteToText(f'./data/{self.table}', file_name_suffix='.txt')
        
        return f'{self.step_label}-writer' >> writer
