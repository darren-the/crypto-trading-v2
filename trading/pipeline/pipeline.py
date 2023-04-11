# Config variables and utils
from pipeline.configs import config
from pipeline.utils.utils import date_str_to_timestamp

# Import candle steps
from pipeline.steps.candles.fetch_candles import FetchCandles
from pipeline.steps.candles.aggregate_candles import AggregateCandles

# Import transformers
from pipeline.steps.transformers.high_low import HighLow
from pipeline.steps.transformers.rsi import RSI
from pipeline.steps.transformers.retracement import Retracement
from pipeline.steps.transformers.high_low_history import HighLowHistory
from pipeline.steps.transformers.avg_rsi import AvgRSI
from pipeline.steps.transformers.dev.trader import Trader
from pipeline.steps.transformers.structure import Structure
from pipeline.steps.transformers.rsi_projection import RSIProjection

# Import combiners
from pipeline.steps.combiners.retracement_long import RetracementLong
from pipeline.steps.combiners.support_combiner import SupportCombiner

# Import aggregators
from pipeline.steps.aggregators.aggregate_retracement_long import AggregateRetracementLong
from pipeline.steps.aggregators.aggregate_buy_sell import AggregateBuySell

import os

from pipeline.base_classes.source import Source


def run(pipeline_id):
    os.environ['PIPELINE_ID'] = str(pipeline_id)
    os.environ['PIPELINE_START'] = str(date_str_to_timestamp(config.dev_hist_start))
    os.environ['PIPELINE_END'] = str(date_str_to_timestamp(config.dev_hist_end))

    # Symbol task objects
    fetch_candles = {}
    for s in config.symbols:
        fetch_candles[s] = FetchCandles(
            symbol=s,
            ignore_pipeline_id=True
        )

        # Timeframe task objects
        aggregate_candles = {s: {}}
        high_low = {s: {}}
        rsi = {s: {}}
        high_low_history = {s: {}}
        structure = {s: {}}
        rsi_projection = {s: {}}

        for t in config.timeframes:
            # Defining tasks
            aggregate_candles[s][t] = AggregateCandles(
                symbol=s,
                timeframe=t,
            )

            high_low[s][t] = HighLow(
                symbol=s,
                timeframe=t,
                pivot=5,
            )

            rsi[s][t] = RSI(
                symbol=s,
                timeframe=t,
                max_length=14
            )

            high_low_history[s][t] = HighLowHistory(
                symbol=s,
                timeframe=t,
                history_length=10,
            )

            rsi_projection[s][t] = RSIProjection(
                symbol=s,
                timeframe=t,
                rsi_projection=30,
            )

            structure[s][t] = Structure(
                symbol=s,
                timeframe=t,
            )

            # set dependencies at a timeframe level
            fetch_candles[s] >> aggregate_candles[s][t] >> [high_low[s][t], rsi[s][t]]
            high_low[s][t] >> [high_low_history[s][t], structure[s][t]]
            rsi[s][t] >> rsi_projection[s][t]

        # set dependencies at a symbol level here

    source = Source()
    source.start_source()
    