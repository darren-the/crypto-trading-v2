import apache_beam as beam
import pipeline.config as config


pipeline_step_options = {
    'symbol': None,
    'timeframe': None,
    'writer': 'TEXT',
}

class PipelineStep(beam.PTransform):
    """
    TODO: Add description
    """

    def __init__(self, dofn: type[beam.DoFn]):
        self.dofn = dofn
        self.config_name = str(type(dofn).__name__).lower()
        self.table = f'{pipeline_step_options["symbol"]}.{config.table[self.config_name]}-{pipeline_step_options["timeframe"]}'
        self.text_dest = self.table.replace('.', '-')
        self.bq_dest = self.table
        self.schema = config.schema[self.config_name]

    def expand(self, pcoll):
        writer = self._get_writer()
        writer_label = f'{self.table}-writer'
        dofn_label = f'{self.table}-dofn'

        # Data will continue flowing through main branch
        main_branch = pcoll | dofn_label >> beam.ParDo(self.dofn)

        # create a separate branch to write data
        main_branch | writer_label >> writer  

        return main_branch

    def _get_writer(self):
        if pipeline_step_options['writer'] == 'TEXT':
            return beam.io.WriteToText(f'./data/{self.text_dest}', file_name_suffix='.txt')
        elif pipeline_step_options['writer'] == 'BIGQUERY':
            return beam.io.WriteToBigQuery(
                table=self.bq_dest,
                schema={'fields': self.schema},
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        raise Exception(f'\'{pipeline_step_options["writer"]}\' is an invalid writer in pipeline_step_options')
