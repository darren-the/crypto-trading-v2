import requests
from app.common.common_utils import timeframe_to_ms, load_config
import time
from app.pipeline.base_classes.task import Task


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
        super().__init__()
        self.prev_timestamp = self._get_prev_timestamp()  # requires start variable

    def generate(self):
        yield from self._fetch_batch_candles()
        yield from self._empty_candle_gen()

    def _create_url(self):
        base_url = self.exch_conf["base_url"]
        base_url = base_url.replace(f"[TIMEFRAME]", conf["base_timeframe"])
        base_url = base_url.replace(f"[SYMBOL]", self.symbol)
        base_url = base_url.replace(f"[UPDATE_METHOD]", "hist")  # bitfinex specific param
        return base_url
    
    def _get_prev_timestamp(self):
        payload = {
            'end': self.start - self.interval,
            'limit': 1,
        }
        try:
            candles = requests.get(self.url, params=payload).json()
        except:
            raise Exception(f'''
                Invalid request.\n
                Arguments:\n
                \turl: {self.url}\n
                \tparams: {str(payload)}\n
            ''')
        if len(candles) > 0:
            return candles[0][0]
        return None
    
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
        for i in range(self.start, self.end, self.limit * self.interval):
            batch_start = i
            batch_end = min(i + self.limit * self.interval, self.end)
            candles = self._fetch_candles(batch_start, batch_end)
            for candle in candles:
                element = {
                    "exchange": self.exchange,
                    "symbol": self.symbol,
                    "timeframe": conf["base_timeframe"],
                    'timestamp': candle[0],
                    'open': candle[1],
                    'close': candle[2],
                    'high': candle[3],
                    'low': candle[4],
                    "prev_timestamp": self.prev_timestamp
                }
                if self.prev_timestamp is not None and element["timestamp"] > self.prev_timestamp:
                    yield element
                self.prev_timestamp = element["timestamp"]

            # Calculate length of time delay to not breach req limit
            # TODO: technically we should be calling the API through our own API build
            # this could then track the number of requests properly, regardless of symbol.
            # This delay would only come in affect once our API is bottlenecked.
            delay = 60 * len(conf["symbols"]) / self.exch_conf["max_req_per_min"]
            time.sleep(delay)
    
    def _empty_candle_gen(self):
        # Generate None's to fill gap till end timestamp
        for _ in range(self.prev_timestamp, self.end, self.interval):
            yield None