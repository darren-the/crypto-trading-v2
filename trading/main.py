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
    # Defining source
    fetch_candles = FetchCandles(config.local_hist_start, config.local_hist_end)

    for symbol in config.symbols:
        for timeframe in config.timeframes:
            # Defining tasks
            aggregate_candles = AggregateCandles(
                symbol=symbol,
                timeframe=timeframe,
                write_output=True
            )

            # Organise dependencies
            fetch_candles >> aggregate_candles
    
    fetch_candles.activate()
                

if __name__ == '__main__':
    run()
