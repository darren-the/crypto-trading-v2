from pipeline.base_classes.task import Task
from pipeline.configs.constants import MARKET_BUY, MARKET_SELL, MARKET_STOP_SELL, LIMIT_SELL
import json

class AggregateBuySell(Task):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.buy = False
        self.sell = False
        super().__init__()

    def process(self, element):
        for order_type in json.loads(element['transaction_summary']):
            if order_type == MARKET_BUY:
                self.buy = True
            elif order_type == MARKET_SELL or order_type == MARKET_STOP_SELL or order_type == LIMIT_SELL:
                self.sell = True
        agg_buy_sell = {
            'timestamp': element['timestamp'],
            'candle_timestamp': element['candle_timestamp'],
            'agg_buy': self.buy,
            'agg_sell': self.sell,
            'is_complete': element['is_complete'],
        }
        if element['is_complete']:
            self.buy = False
            self.sell = False
        return agg_buy_sell
