import requests
from app.common.common_utils import timeframe_to_ms, load_config
import time
from app.pipeline.base_classes.task import Task
from copy import deepcopy


conf = load_config()

class FetchCandles(Task):
    def __init__(self, *args, **kwargs):
        self.symbol = ""
        self.exchange = ""
        self.__dict__.update(kwargs)
        self.exch_conf = load_config(self.exchange)
        self.url = self._create_url()
        self.limit = self.exch_conf["max_data_per_req"]
        self.interval = timeframe_to_ms(conf["base_timeframe"])
        self.table_name = "base_candles"
        self.last_candle = None
        self.final_batch_flag = False

        super().__init__()
        self.fetch_end = self.end - self.interval

    def generate(self):
        yield from self._fetch_batch_candles()

    def _create_url(self):
        base_url = self.exch_conf["base_url"]
        base_url = base_url.replace(f"[TIMEFRAME]", conf["base_timeframe"])
        base_url = base_url.replace(f"[SYMBOL]", self.symbol)
        base_url = base_url.replace(f"[UPDATE_METHOD]", "hist")  # bitfinex specific param
        return base_url
    
    def _fetch_candles(self, start, end):
        payload = {
            'start': start,
            'end': end,
            'sort': 1,
            'limit': self.limit,
        }
        try:
            return requests.get(self.url, params=payload).json()
        except:
            raise Exception(f'''
                Invalid request.\n
                Arguments:\n
                \turl: {self.url}\n
                \tparams: {str(payload)}\n
            ''')
    
    def _fetch_batch_candles(self):
        for i in range(self.start, self.fetch_end, self.limit * self.interval):
            batch_start = i
            batch_end = min(i + self.limit * self.interval, self.fetch_end)
            if batch_end == self.fetch_end:
                self.final_batch_flag = True
            candles = self._fetch_candles(batch_start, batch_end)
            yield from self._clean_candles(candles)

            # Calculate length of time delay to not breach req limit
            # TODO: technically we should be calling the API through our own API build
            # this could then track the number of requests properly, regardless of symbol.
            # This delay would only come in affect once our API is bottlenecked.
            delay = 60 / self.exch_conf["max_req_per_min"]
            time.sleep(delay)

    def _format_candle(self, raw_candle):
        return {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "timeframe": conf["base_timeframe"],
            'timestamp': raw_candle[0],
            'open': raw_candle[1],
            'close': raw_candle[2],
            'high': raw_candle[3],
            'low': raw_candle[4],
        }

    def _clean_candles(self, candles):
        '''
        Format candles and impute missing data with 1) previous candle, or if that doesn't exist
        then 2) the next candle.
        '''
        for i in range(len(candles)):
            candle = candles[i]
            element = self._format_candle(candle)

            # Skip duplicates
            if self.last_candle is not None and self.last_candle['timestamp'] == element['timestamp']:
                continue

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
            yield element

            # Check whether there is a gap between the last candle and the end timestamp
            if self.final_batch_flag and i == len(candles) - 1:
                for t in range(self.last_candle['timestamp'] + self.interval, self.end, self.interval):
                    last_copy = deepcopy(self.last_candle)
                    last_copy['timestamp'] = t
                    yield last_copy
