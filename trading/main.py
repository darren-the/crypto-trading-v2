# Config variables and utils
from configs import config

# Import candle steps
from steps.candles.fetch_candles import FetchCandles
from steps.candles.aggregate_candles import AggregateCandles

# Import transformers
from steps.transformers.high_low import HighLow
from steps.transformers.resistance import Resistance
from steps.transformers.support import Support
from steps.transformers.rsi import RSI

# Other libraries
import argparse
import logging


def run():
    fetch_candles = {}
    for s in config.symbols:
        fetch_candles[s] = FetchCandles(s, config.local_hist_start, config.local_hist_end)

        # Base tasks objects
        aggregate_candles = {s: {}}
        high_low = {s: {}}
        rsi = {s: {}}
        resistance = {s: {}}
        support = {s: {}}

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

            # Organise dependencies
            fetch_candles[s] >> aggregate_candles[s][t] >> [high_low[s][t], rsi[s][t]]
            high_low[s][t] >> [resistance[s][t], support[s][t]]
    
    for s in config.symbols:
        fetch_candles[s].activate()

if __name__ == '__main__':
    run()
