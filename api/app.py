from flask import Flask, request
from google.cloud import bigquery
import pandas as pd
import decimal
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
client = bigquery.Client()


@app.route('/candles', methods=['GET'])
def candles():
    # Require args
    args = request.args
    required_args = ['timeframe', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    QUERY = f'''
        SELECT
            candle_timestamp
            , open
            , close
            , high
            , low
        FROM `crypto-trading-v2.BTCUSD.candles-{args.get('timeframe')}`
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY candle_timestamp
            ORDER BY timestamp DESC
        ) = 1
        ORDER BY timestamp
        LIMIT 10000
    '''
    job = client.query(QUERY)
    try:
        results = job.result()
    except:
        return {'error': job.errors}, 400
    df = results.to_dataframe()
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return {'data': df.values.tolist()}, 200

@app.route('/highs', methods=['GET'])
def highs():
    # Require args
    args = request.args
    required_args = ['timeframe', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    QUERY = f'''
        SELECT high_timestamp
        FROM `crypto-trading-v2.BTCUSD.high-low-{args.get('timeframe')}`
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
            AND is_high = TRUE
        ORDER BY timestamp
        LIMIT 10000
    '''
    job = client.query(QUERY)
    try:
        results = job.result()
    except:
        return {'error': job.errors}, 400
    df = results.to_dataframe()
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return {'data': df.high_timestamp.values.tolist()}, 200

@app.route('/lows', methods=['GET'])
def lows():
    # Require args
    args = request.args
    required_args = ['timeframe', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    QUERY = f'''
        SELECT low_timestamp
        FROM `crypto-trading-v2.BTCUSD.high-low-{args.get('timeframe')}`
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
            AND is_low = TRUE
        ORDER BY timestamp
        LIMIT 10000
    '''
    job = client.query(QUERY)
    try:
        results = job.result()
    except:
        return {'error': job.errors}, 400
    df = results.to_dataframe()
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return {'data': df.low_timestamp.values.tolist()}, 200

@app.route('/resistance', methods=['GET'])
def resistance():
    # Require args
    args = request.args
    required_args = ['timeframe', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    QUERY = f'''
        SELECT
            candle_timestamp
            , top_history
        FROM `crypto-trading-v2.BTCUSD.resistance-{args.get('timeframe')}`
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY candle_timestamp
            ORDER BY timestamp DESC
        ) = 1
        ORDER BY candle_timestamp
        LIMIT 10000
    '''
    job = client.query(QUERY)
    try:
        results = job.result()
    except:
        return {'error': job.errors}, 400
    df = results.to_dataframe()
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return {'data': df.values.tolist()}, 200

@app.route('/support', methods=['GET'])
def support():
    # Require args
    args = request.args
    required_args = ['timeframe', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    QUERY = f'''
        SELECT
            candle_timestamp
            , bottom_history
        FROM `crypto-trading-v2.BTCUSD.support-{args.get('timeframe')}`
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY candle_timestamp
            ORDER BY timestamp DESC
        ) = 1
        ORDER BY candle_timestamp
        LIMIT 10000
    '''
    job = client.query(QUERY)
    try:
        results = job.result()
    except:
        return {'error': job.errors}, 400
    df = results.to_dataframe()
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return {'data': df.values.tolist()}, 200

@app.route('/rsi', methods=['GET'])
def rsi():
    # Require args
    args = request.args
    required_args = ['timeframe', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    QUERY = f'''
        SELECT
            candle_timestamp
            , rsi
        FROM `crypto-trading-v2.BTCUSD.rsi-{args.get('timeframe')}`
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY candle_timestamp
            ORDER BY timestamp DESC
        ) = 1
        ORDER BY timestamp
        LIMIT 10000
    '''
    job = client.query(QUERY)
    try:
        results = job.result()
    except:
        return {'error': job.errors}, 400
    df = results.to_dataframe()
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return {'data': df.values.tolist()}, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
