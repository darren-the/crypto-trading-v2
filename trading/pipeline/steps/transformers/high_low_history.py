from pipeline.base_classes.task import Task


class HighLowHistory(Task):
    '''
    Currently a temporary class used to help interpret the HighLow outputs.
    For now it will be treated separately to the transformer until the use cases are
    understood better and its determined that this is a more appropriate format for the HighLow outputs.
    '''
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.history = []
        super().__init__()

    def process(self, element):
        high = self._get_high(element) if element['high_timestamp'] != -1 else None
        low = self._get_low(element) if element['low_timestamp'] != -1 else None

        # Remove any unconfirmed highs/lows
        keep_until_index = len(self.history)
        for i in range(len(self.history) - 1, -1, -1):
            if not self.history[i]['confirmed']:
                keep_until_index = i
            else:
                break
        self.history = self.history[:keep_until_index]

        # Append high and low in time order
        if high is not None and low is not None:
            if high['timestamp'] < low['timestamp'] or (
                high['timestamp'] == low['timestamp'] and \
                element['open'] > element['close']
            ):
                self.history.append(high)
                self.history.append(low)
            if low['timestamp'] < high['timestamp'] or (
                high['timestamp'] == low['timestamp'] and \
                element['close'] > element['open']
            ):
                self.history.append(low)
                self.history.append(high)
        elif high is not None:
            self.history.append(high)
        elif low is not None:
            self.history.append(low)
        
        # Maintain history length
        while len(self.history) > self.history_length:
            self.history.pop(0)

        # Format into a storable and parsable object
        high_timestamps = []
        low_timestamps = []
        high_low_types = []
        high_low_timestamps = []
        high_low_prices = []
        for hl in self.history:
            high_low_types.append(hl['type'])
            high_low_timestamps.append(str(hl['timestamp']))
            if hl['type'] == 'high':
                high_timestamps.append(str(hl['timestamp']))
                high_low_prices.append(str(hl['top']))
            else:
                low_timestamps.append(str(hl['timestamp']))
                high_low_prices.append(str(hl['bottom']))

        return {
            'timestamp': element['timestamp'],
            'candle_timestamp': element['candle_timestamp'],
            'high_timestamp_history': ','.join(high_timestamps),
            'low_timestamp_history': ','.join(low_timestamps),
            'high_low_type_history': ','.join(high_low_types),
            'high_low_timestamp_history': ','.join(high_low_timestamps),
            'high_low_price_history': ','.join(high_low_prices),
        }
        

    def _get_high(self, element):
        return {
            'type': 'high',
            'confirmed': element['is_high'],
            'timestamp': element['high_timestamp'],
            'top': element['high_top'],
            'bottom': element['high_bottom'],
        }
    
    def _get_low(self, element):
        return {
            'type': 'low',
            'confirmed': element['is_low'],
            'timestamp': element['low_timestamp'],
            'top': element['low_top'],
            'bottom': element['low_bottom'],
        }