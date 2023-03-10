import apache_beam as beam


# Relative Strength Index calculation. Source: https://www.investopedia.com/terms/r/rsi.asp
class RSI(beam.DoFn):
    def __init__(self, max_length=14):
        self.last_price = -1
        self.previous_avg_gain = -1
        self.previous_avg_loss = -1
        self.max_length = max_length
        self.current_length = 0
        
    def process(self, element):
        rsi_value = avg_gain = avg_loss = -1
        
        if self.last_price > 0:
            # Calculate rsi value
            price_change = element['close'] - self.last_price
            gain = price_change if price_change > 0 else 0
            loss = -price_change if price_change < 0 else 0
            avg_gain = (self.previous_avg_gain * (self.current_length - 1) + gain) / self.current_length
            avg_loss = (self.previous_avg_loss * (self.current_length - 1) + loss) / self.current_length
            rsi_value = 100 - 100 / (1 + avg_gain / avg_loss if avg_loss != 0 else 1)

        # update variables if candlestick is complete
        if element['is_complete']:
            self.last_price = element['close']
            self.previous_avg_gain = avg_gain
            self.previous_avg_loss = avg_loss
            self.current_length += 1 if self.current_length < self.max_length else 0

        rsi = {
            'timestamp': element['timestamp'],
            'candle_timestamp': element['candle_timestamp'],
            'rsi': round(rsi_value, 2),
        }

        yield rsi
