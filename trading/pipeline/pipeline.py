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

    trader = Trader(balance=10000)
    fetch_candles = {}
    retracement_long = {}
    support_combiner = {}
    for s in config.symbols:
        fetch_candles[s] = FetchCandles(
            symbol=s,
            ignore_pipeline_id=True
        )
        retracement_long[s] = RetracementLong(
            symbol=s,
            ignore_timeframes=['1m'],
        )
        support_combiner[s] = SupportCombiner(
            symbol=s,
            ignore_timeframes=['1m'],
        )

        # Base tasks objects
        aggregate_candles = {s: {}}
        high_low = {s: {}}
        rsi = {s: {}}
        retracement = {s: {}}
        high_low_history = {s: {}}
        avg_rsi = {s: {}}
        agg_retracement_long = {s: {}}
        agg_buy_sell = {s: {}}

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

            retracement[s][t] = Retracement(
                symbol=s,
                timeframe=t,
            )

            high_low_history[s][t] = HighLowHistory(
                symbol=s,
                timeframe=t,
                history_length=10,
            )

            avg_rsi[s][t] = AvgRSI(
                symbol=s,
                timeframe=t,
                avg_rsi_length=5,
                scale_upper_bound=70,
                scale_lower_bound=30,
                scale_factor=0.75,
            )

            agg_retracement_long[s][t] = AggregateRetracementLong(
                symbol=s,
                timeframe=t,
            )

            agg_buy_sell[s][t] = AggregateBuySell(
                symbol=s,
                timeframe=t,
            )

            # set dependencies at a timeframe level
            fetch_candles[s] >> aggregate_candles[s][t] >> [high_low[s][t], rsi[s][t]]
            high_low[s][t] >> high_low_history[s][t]
            [aggregate_candles[s][t], high_low_history[s][t]] >> retracement[s][t]
            rsi[s][t] >> avg_rsi[s][t]
            [aggregate_candles[s][t], retracement_long[s]] >> agg_retracement_long[s][t]
            [aggregate_candles[s][t], trader] >> agg_buy_sell[s][t]
        
        # set dependencies at a symbol level
        [
            *rsi[s].values(),
            *retracement[s].values(),
            *avg_rsi[s].values(),
            aggregate_candles[s][config.base_timeframe],
        ] >> retracement_long[s]
        [*high_low[s].values(), retracement_long[s]] >> support_combiner[s]
        [retracement_long[s], aggregate_candles[s][config.base_timeframe], support_combiner[s]] >> trader


    source = Source()
    source.start_source()
    