from pipeline.base_classes.timeframe_combiner import TimeframeCombiner
from pipeline.configs import config
import json


class StructureCombiner(TimeframeCombiner):
    def __init__(self, *args, **kwargs):
        self.ignore_timeframes = []
        self.__dict__.update(kwargs)

        # Identify timeframes to process but in reverse
        self.reversed_timeframes = list(reversed(config.timeframes))
        for t in self.ignore_timeframes:
            self.reversed_timeframes.remove(t)

        super().__init__()

    def process(self, element):
        # find min structure break
        pass

    def _max_timeframe_break(self, element):
        max_timeframe = 'no_timeframe'
        for t in self.reversed_timeframes:
            if element[t]['struct_top'] == -1 and element:
                pass
            passasdasdasd