from pipeline.base_classes.task import Task


class AggregateRetracementLong(Task):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.retracement_long = False
        super().__init__()

    def process(self, element):
        if element['retracement_long']:
            self.retracement_long = True
        agg_retracement_long = {
            'timestamp': element['timestamp'],
            'candle_timestamp': element['candle_timestamp'],
            'agg_retracement_long': self.retracement_long,
            'is_complete': element['is_complete'],
        }
        if element['is_complete']:
            self.retracement_long = False
        return agg_retracement_long
