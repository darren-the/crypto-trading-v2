local_env_data = './data'
symbols = ['BTCUSD']
timeframes = ['1m']
table = {
    'fetchcandles': 'candles',
}
schema = {
    'fetchcandles': [
        {'name': 'timestamp', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'open', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'close', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'high', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
        {'name': 'low', 'type': 'NUMERIC', 'mode': 'REQUIRED'},
    ]
}