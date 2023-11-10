# Config variables and utils
from app.common.common_utils import date_str_to_timestamp, load_config

# Import candle steps
from app.pipeline.steps.candles.fetch_candles import FetchCandles

import os

from app.pipeline.base_classes.master import Master


conf = load_config()

def run():
    os.environ['ENV_TYPE'] = 'local'
    os.environ['PIPELINE_START'] = str(date_str_to_timestamp(conf["hist_start_date"]))
    os.environ['PIPELINE_END'] = str(date_str_to_timestamp(conf["hist_end_date"]))
    EXCHANGE = "bitfinex"

    # Symbol task objects
    fetch_candles = {}
    clean_candles = {}
    for s in conf["symbols"]:
        fetch_candles[s] = FetchCandles(
            exchange=EXCHANGE, symbol=s, ignore_pipeline_id=True)
        # clean_candles[s] = CleanCandles(symbol=s)

        # Timeframe task objects
        # e.g. aggregate_candles = {s: {}}

        for t in conf["timeframes"]:
            # Defining tasks
            # E.g. aggregate_candles[s][t] = AggregateCandles(symbol=s, timeframe=t)

            # set dependencies at a timeframe level
            # e.g. fetch_candles[s] >> aggregate_candles[s][t]
            pass

    master = Master()
    master.start_pipeline()

    # maybe source.backfill()

run()
