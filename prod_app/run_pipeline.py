# Config variables and utils
from app.common.common_utils import date_str_to_timestamp, load_config

# Import candle steps
from app.pipeline.steps.candles.fetch_candles import FetchCandles
from app.pipeline.steps.candles.aggregate_candles import AggregateCandles

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
            exchange=EXCHANGE,
            symbol=s
        )

        aggregate_candles = {s: {}}

        for t in conf["timeframes"]:
            aggregate_candles[s][t] = AggregateCandles(
                exchange=EXCHANGE,
                symbol=s,
                timeframe=t
            )

            fetch_candles[s] >> aggregate_candles[s][t]

    master = Master()
    master.start_pipeline()

    # maybe source.backfill()

run()
