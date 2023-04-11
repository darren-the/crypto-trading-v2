from pipeline.base_classes.task import Task
from pipeline.utils.utils import timeframe_to_ms


class RSIProjection(Task):
    def __init__(self, *args, **kwargs):
        self.rsi_projection = 30
        self.__dict__.update(kwargs)
        super().__init__()
        
    def process(self, element):
        price_projection = candle_timestamp_projection = -1

        if element['last_price'] > 0:
            # Reverse rsi value
            reverse_avg_loss = self.rsi_projection * element['previous_avg_loss'] * (element['current_rsi_length'] - 1)
            reverse_avg_gain = (100 - self.rsi_projection) * element['previous_avg_gain'] * (element['current_rsi_length'] - 1)
            reverse_avg_gain_loss_diff = reverse_avg_loss - reverse_avg_gain
            if reverse_avg_gain_loss_diff > 0:
                loss = 0
                gain = reverse_avg_gain_loss_diff / (100 - self.rsi_projection)
            elif reverse_avg_gain_loss_diff < 0:
                gain = 0
                loss = reverse_avg_gain_loss_diff / self.rsi_projection
            else:
                gain = loss = 0
            price_change = gain if gain > 0 else loss
            price_projection = element['last_price'] + price_change
            candle_timestamp_projection = element['candle_timestamp'] if not element['is_complete'] \
                else element['candle_timestamp'] + timeframe_to_ms(self.timeframe)

        return {
            'timestamp': element['timestamp'],
            'candle_timestamp': element['candle_timestamp'],
            'candle_timestamp_projection': candle_timestamp_projection,
            'price_projection': round(price_projection, 4),
            'is_complete': element['is_complete'],
        }
