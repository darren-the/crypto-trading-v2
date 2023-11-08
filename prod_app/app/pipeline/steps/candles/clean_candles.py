from app.common.common_utils import timeframe_to_ms, load_config
from app.pipeline.base_classes.task import Task
from copy import deepcopy


conf = load_config()

class CleanCandles(Task):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.interval = timeframe_to_ms(conf["base_timeframe"])
        self.last_candle = None
        self.table_name = "base_candles_cleaned"
        super().__init__()

    def process(self, element):
        # Check whether the first candles are missing
        if self.last_candle is None and element['timestamp'] != self.start:
            # Copy the OCHL data from the next most available candle
            for t in range(self.start, element['timestamp'], self.interval):
                element_copy = deepcopy(element)
                element_copy['timestamp'] = t
                yield element_copy

        # Check whether other candles are missing
        elif self.last_candle is not None and element['timestamp'] - self.last_candle['timestamp'] > self.interval:
            # Copy the OCHL data from the last available candle
            for t in range(self.last_candle['timestamp'] + self.interval, element['timestamp'], self.interval):
                last_copy = deepcopy(self.last_candle)
                last_copy['timestamp'] = t
                yield last_copy

                
        self.last_candle = element

            # TODO: Minor enhancement: Check whether cancldes are missing between element and last WHEN we are at the final candle