local_env_data = './data'
symbols = ['BTCUSD']
timeframes = [
    '1m',
    # '5m',
    # '15m',
    # '30m',
    # '1h',
    # '2h',
    # '4h',
    # '6h',
    # '12h',
    # '1D',
    # '2D',
]
table = {
    'aggregatecandles': 'candles',
}
schema = {
    'aggregatecandles': [
        {'name': 'timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'open', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'close', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'high', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'low', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'rank', 'type': 'INT64', 'mode': 'REQUIRED'}
    ]
}
default_hist_start = '2022-01-01'
default_hist_end = '2022-02-01'
bitfinex = {
    'base_url': 'https://api-pub.bitfinex.com/v2',
    'candles': {
        'base_url': 'https://api-pub.bitfinex.com/v2/candles/trade:1m:tBTCUSD/hist',
        'max_data_per_req': 10000,
        'max_req_per_min': 90,
    },
}
