from flask import Flask, request
from google.cloud import bigquery
import pandas as pd
import decimal


app = Flask(__name__)

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

    client = bigquery.Client()
    QUERY = f'''
        SELECT
            timestamp
            , open
            , close
            , high
            , low
        FROM `crypto-trading-v2.BTCUSD.candles-{args.get('timeframe')}`
        WHERE timestamp BETWEEN {args.get('start')} AND {args.get('end')}
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY timestamp
            ORDER BY rank DESC
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