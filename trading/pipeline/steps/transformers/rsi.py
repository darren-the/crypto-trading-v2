from pipeline.base_classes.task import Task


# Relative Strength Index calculation. Source: https://www.investopedia.com/terms/r/rsi.asp
class RSI(Task):
    def __init__(self, *args, **kwargs):
        self.max_length = 14
        self.__dict__.update(kwargs)
        self.last_price = -1
        self.previous_avg_gain = -1
        self.previous_avg_loss = -1
        self.current_rsi_length = 0
        super().__init__()
        
    def process(self, element):
        rsi_value = avg_gain = avg_loss = -1
        
        if self.last_price > 0:
            # Calculate rsi value
            price_change = element['close'] - self.last_price
            gain = price_change if price_change > 0 else 0
            loss = -price_change if price_change < 0 else 0
            avg_gain = (self.previous_avg_gain * (self.current_rsi_length - 1) + gain) / self.current_rsi_length
            avg_loss = (self.previous_avg_loss * (self.current_rsi_length - 1) + loss) / self.current_rsi_length
            rsi_value = 100 - 100 / (1 + avg_gain / avg_loss if avg_loss != 0 else 1)

        # update variables if candlestick is complete
        if element['is_complete']:
            self.last_price = element['close']
            self.previous_avg_gain = avg_gain
            self.previous_avg_loss = avg_loss
            self.current_rsi_length += 1 if self.current_rsi_length < self.max_length else 0

        rsi = {
            'timestamp': element['timestamp'],
            'candle_timestamp': element['candle_timestamp'],
            'rsi': round(rsi_value, 2),
            'last_price': self.last_price,
            'previous_avg_gain': self.previous_avg_gain,
            'previous_avg_loss': self.previous_avg_loss,
            'current_rsi_length': self.current_rsi_length,
            'is_complete': element['is_complete'],
        }

        return rsi
