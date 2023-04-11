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
    '1W',
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
    'retracementlong': 'retracement_long',
    'aggregateretracementlong': 'aggregate_retracement_long',
    'supportcombiner': 'support_combiner',
    'trader': 'trader',
    'aggregatebuysell': 'aggregate_buy_sell',
    'structure': 'structure',
    'rsiprojection': 'rsi_projection',
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
        'high_id NUMERIC NOT NULL',
        'high_timestamp NUMERIC NOT NULL',
        'high_top NUMERIC NOT NULL',
        'high_bottom NUMERIC NOT NULL',
        'high_colour TEXT NOT NULL',
        'is_low BOOL NOT NULL',
        'low_id NUMERIC NOT NULL',
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
        'last_price NUMERIC NOT NULL',
        'previous_avg_gain NUMERIC NOT NULL',
        'previous_avg_loss NUMERIC NOT NULL',
        'current_rsi_length NUMERIC NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'retracement': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'high_retracement NUMERIC NOT NULL',
        'high_retracement_high NUMERIC NOT NULL',
        'high_retracement_low NUMERIC NOT NULL',
        'low_retracement NUMERIC NOT NULL',
        'low_retracement_high NUMERIC NOT NULL',
        'low_retracement_low NUMERIC NOT NULL',
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
    'retracementlong': [
        'timestamp NUMERIC PRIMARY KEY',
        'retracement_timeframe TEXT NOT NULL',
        'high_retracement NUMERIC NOT NULL',
        'oversold_timeframe TEXT NOT NULL',
        'avg_rsi NUMERIC NOT NULL',
        'support_range TEXT NOT NULL',
        'reward_price NUMERIC NOT NULL',
        'risk_delta NUMERIC NOT NULL',
        'retracement_long BOOL NOT NULL',
    ],
    'aggregateretracementlong': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'agg_retracement_long BOOL NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'supportcombiner': [
        'timestamp NUMERIC PRIMARY KEY',
        'supports TEXT NOT NULL',
    ],
    'support_history_log': [
        'timestamp NUMERIC NOT NULL',
        'time TIMESTAMP NOT NULL',
        'sup_id NUMERIC NOT NULL',
        'last_update NUMERIC NOT NULL',
        'max_timeframe TEXT NOT NULL',
        'start_timestamp NUMERIC NOT NULL',
        'end_timestamp NUMERIC NOT NULL',
        'sup_factor NUMERIC NOT NULL',
        'sup_top NUMERIC NOT NULL',
        'sup_bottom NUMERIC NOT NULL',
    ],
    'trader': [
        'timestamp NUMERIC PRIMARY KEY',
        'balance NUMERIC NOT NULL',
        'equity NUMERIC NOT NULL',
        'position_base_price NUMERIC NOT NULL',
        'position_amount NUMERIC NOT NULL',
        'orders TEXT NOT NULL',
        'transaction_summary TEXT NOT NULL',
        'recent_sup_top NUMERIC NOT NULL',
        'recent_sup_bottom NUMERIC NOT NULL',
        'risk NUMERIC NOT NULL',
    ],
    'transaction_history': [
        'timestamp NUMERIC NOT NULL',
        'order_type NUMERIC NOT NULL',
        'price NUMERIC NOT NULL',
        'amount NUMERIC NOT NULL',
    ],
    'aggregatebuysell': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'agg_buy BOOL NOT NULL',
        'agg_sell BOOL NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'structure': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'struct_start_timestamp NUMERIC NOT NULL',
        'struct_end_timestamp NUMERIC NOT NULL',
        'struct_top NUMERIC NOT NULL',
        'equil_top NUMERIC NOT NULL',
        'struct_bottom NUMERIC NOT NULL',
        'equil_bottom NUMERIC NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
    'rsiprojection': [
        'timestamp NUMERIC PRIMARY KEY',
        'candle_timestamp NUMERIC NOT NULL',
        'candle_timestamp_projection NUMERIC NOT NULL',
        'price_projection NUMERIC NOT NULL',
        'is_complete BOOL NOT NULL',
    ],
}
dev_hist_start = '2021-11-27'
dev_hist_end = '2022-05-08'
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
weekly_start_date = '2011-08-15'  # based on bitstamp earliest history