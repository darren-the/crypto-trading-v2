from pipeline.base_classes.task import Task
import numpy as np
from scipy.stats import spearmanr
from copy import deepcopy


class HighLow(Task):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.current_candles = []
        self.is_high = False
        self.high_timestamp = -1
        self.high_top = -1
        self.high_bottom = -1
        self.is_low = False
        self.low_timestamp = -1
        self.low_top = -1
        self.low_bottom = -1
        self.alpha = 0
        super().__init__()

    def process(self, element):
        

        if element['is_complete']:
            