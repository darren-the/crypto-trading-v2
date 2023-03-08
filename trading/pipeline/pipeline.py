# Config variables and utils
from pipeline.configs import config
from pipeline.utils.utils import date_str_to_timestamp

# Import candle steps
from pipeline.steps.candles.fetch_candles import FetchCandles
from pipeline.steps.candles.aggregate_candles import AggregateCandles

# Import transformers
from pipeline.steps.transformers.high_low import HighLow
from pipeline.steps.transformers.resistance import Resistance
from pipeline.steps.transformers.support import Support
from pipeline.steps.transformers.rsi import RSI
from pipeline.steps.transformers.retracement import Retracement

import os


def run(pipeline_id):
    os.environ['PIPELINE_ID'] = str(pipeline_id)
    os.environ['PIPELINE_START'] = str(date_str_to_timestamp(config.local_hist_start))
    os.environ['PIPELINE_END'] = str(date_str_to_timestamp(config.local_hist_end))

    fetch_candles = {}
    for s in config.symbols:
        fetch_candles[s] = FetchCandles(s)

        # Base tasks objects
        aggregate_candles = {s: {}}
        high_low = {s: {}}
        rsi = {s: {}}
        resistance = {s: {}}
        support = {s: {}}
        retracement = {s: {}}

        for t in config.timeframes:
            # Defining tasks
            aggregate_candles[s][t] = AggregateCandles(
                symbol=s,
                timeframe=t,
                write_output=True
            )

            high_low[s][t] = HighLow(
                symbol=s,
                timeframe=t,
                write_output=True,
                pivot=5,
            )

            rsi[s][t] = RSI(
                symbol=s,
                timeframe=t,
                write_output=True,
                max_length=14
            )

            resistance[s][t] = Resistance(
                symbol=s,
                timeframe=t,
                write_output=True,
                history_length=10
            )

            support[s][t] = Support(
                symbol=s,
                timeframe=t,
                write_output=True,
                history_length=10
            )

            # retracement[s][t] = Retracement(
            #     symbol=s,
            #     timeframe=t,
            #     write_output=True,
            # )

            # Organise dependencies
            fetch_candles[s] >> aggregate_candles[s][t] >> [high_low[s][t], rsi[s][t]]
            high_low[s][t] >> [resistance[s][t], support[s][t]]
    
    for s in config.symbols:
        fetch_candles[s].activate()
