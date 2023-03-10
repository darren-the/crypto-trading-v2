local_env_data = './data'
symbols = ['BTCUSD']
timeframes = [
    '1m',
    '5m',
    '15m',
    # '30m',
    '1h',
    # '2h',
    '4h',
    # '6h',
    # '12h',
    '1D',
    # '2D',
]
base_timeframe = '1m'
base_ms = 60_000
table = {
    'aggregatecandles': 'candles',
    'highlow': 'high-low',
    'resistance': 'resistance',
    'support': 'support',
    'rsi': 'rsi',
}
schema = {
    'basecandles': [
        {'name': 'timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'open', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'close', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'high', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'low', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
    ],
    'aggregatecandles': [
        {'name': 'timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'candle_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'open', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'close', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'high', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'low', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'is_complete', 'type': 'BOOL', 'mode': 'REQUIRED'},
    ],
    'highlow': [
        {'name': 'timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'candle_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'is_high', 'type': 'BOOL', 'mode': 'REQUIRED'},
        {'name': 'high_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'high_top', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'high_bottom', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'is_low', 'type': 'BOOL', 'mode': 'REQUIRED'},
        {'name': 'low_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'low_top', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'low_bottom', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
    ],
    'resistance': [
        {'name': 'timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'candle_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'is_res', 'type': 'BOOL', 'mode': 'REQUIRED'},
        {'name': 'start_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'end_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'num_highs', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'top', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'bottom', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'top_history', 'type': 'STRING', 'mode': 'REQUIRED'},
    ],
    'support': [
        {'name': 'timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'candle_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'is_sup', 'type': 'BOOL', 'mode': 'REQUIRED'},
        {'name': 'start_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'end_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'num_lows', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'top', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'bottom', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'bottom_history', 'type': 'STRING', 'mode': 'REQUIRED'},
    ],
    'rsi': [
        {'name': 'timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'candle_timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'rsi', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
    ]
}
bq_hist_start = '2014-01-01'
bq_hist_end = '2023-01-01'
local_hist_start = '2022-01-01'
local_hist_end = '2022-02-01'
bitfinex = {
    'base_url': 'https://api-pub.bitfinex.com/v2',
    'candle_url': {
        'BTCUSD': 'https://api-pub.bitfinex.com/v2/candles/trade:1m:tBTCUSD/hist'
    },
    'max_data_per_req': 10000,
    'max_req_per_min': 90,
}
