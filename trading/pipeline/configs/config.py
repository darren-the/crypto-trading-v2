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
    'fetchcandles': 'base_candles',
    'aggregatecandles': 'candles',
    'highlow': 'high_low',
    'resistance': 'resistance',
    'support': 'support',
    'rsi': 'rsi',
    'retracement': 'retracement',
    'highlowhistory': 'high_low_history',
    'avgrsi': 'avg_rsi',
}
schema = {
    'fetchcandles': [
        'timestamp NUMERIC PRIMARY KEY',
        'open NUMERIC NOT NULL',
        'close NUMERIC NOT NULL',
        'high NUMERIC NOT NULL',
        'low NUMERIC NOT NULL',
    ],
    'aggregatecandles': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'open NUMERIC NOT NULL',
        'close NUMERIC NOT NULL',
        'high NUMERIC NOT NULL',
        'low NUMERIC NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'highlow': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'is_high BOOL NOT NULL',
        'high_timestamp NUMERIC NOT NULL',
        'high_top NUMERIC NOT NULL',
        'high_bottom NUMERIC NOT NULL',
        'high_colour TEXT NOT NULL',
        'is_low BOOL NOT NULL',
        'low_timestamp NUMERIC NOT NULL',
        'low_top NUMERIC NOT NULL',
        'low_bottom NUMERIC NOT NULL',
        'low_colour TEXT NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'resistance': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'is_res BOOL NOT NULL',
        'start_timestamp NUMERIC NOT NULL',
        'end_timestamp NUMERIC NOT NULL',
        'num_highs NUMERIC NOT NULL',
        'top NUMERIC NOT NULL',
        'bottom NUMERIC NOT NULL',
        'top_history TEXT NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'support': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'is_sup BOOL NOT NULL',
        'start_timestamp NUMERIC NOT NULL',
        'end_timestamp NUMERIC NOT NULL',
        'num_lows NUMERIC NOT NULL',
        'top NUMERIC NOT NULL',
        'bottom NUMERIC NOT NULL',
        'bottom_history TEXT NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'rsi': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'rsi NUMERIC NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'retracement': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'high_retracement NUMERIC NOT NULL',
        'low_retracement NUMERIC NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'highlowhistory': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'high_timestamp_history TEXT NOT NULL',
        'low_timestamp_history TEXT NOT NULL',
        'high_low_type_history TEXT NOT NULL',
        'high_low_timestamp_history TEXT NOT NULL',
        'high_low_price_history TEXT NOT NULL',
        'high_low_confirmed_history TEXT NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'avgrsi': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'avg_rsi NUMERIC NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
}
dev_hist_start = '2022-01-01'
dev_hist_end = '2022-03-01'
bitfinex = {
    'base_url': 'https://api-pub.bitfinex.com/v2',
    'candle_url': {
        'BTCUSD': 'https://api-pub.bitfinex.com/v2/candles/trade:1m:tBTCUSD/hist'
    },
    'max_data_per_req': 10000,
    'max_req_per_min': 90,
}
max_write_batch_size = 10_000
api_base_url = 'http://api:4500'