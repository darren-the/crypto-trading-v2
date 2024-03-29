from flask import Flask, request
from flask_cors import CORS
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
from decimal import Decimal
from utils import timestamp_to_date
import collections
import re


app = Flask(__name__)
CORS(app)
app.config['JSON_SORT_KEYS'] = False

DEC2FLOAT = psycopg2.extensions.new_type(
psycopg2.extensions.DECIMAL.values,
'DEC2FLOAT',
lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)


@app.route('/table_names', methods=['GET'])
def table_names():
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
    """)
    table_names = cur.fetchall()
    cur.close()
    conn.close()

    return {'table_names': table_names}

@app.route('/exists', methods=['GET'])
def table_exists():
    args = request.args
    table_name = args.get('table')

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    cur.execute(f'''
        SELECT EXISTS (
            SELECT *
            FROM information_schema.tables
            WHERE table_name = '{table_name}'
        );
    ''')
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()

    return {'data': query_result[0][0]}

@app.route('/delete_table', methods=['GET'])
def delete_table():
    args = request.args
    table_name = args.get('table')
    pipeline_id = args.get('pipeline_id')
    table_group = args.get('table_group')

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Delete table(s)
    if table_name is not None:
        cur.execute(f'DROP TABLE IF EXISTS {table_name};')
    elif pipeline_id is not None:
        cur.execute(f'''
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name LIKE '%{pipeline_id}';
        ''')
        table_names_to_delete = cur.fetchall()
        for table in table_names_to_delete:
            cur.execute(f'DROP TABLE IF EXISTS {table[0]}')
    elif table_group is not None:
        cur.execute(f'''
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name LIKE '{table_group}%';
        ''')
        table_names_to_delete = cur.fetchall()
        for table in table_names_to_delete:
            cur.execute(f'DROP TABLE IF EXISTS {table[0]}')
    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()

    if table_name is not None:
        return f'Table \'{table_name}\' has been deleted'
    elif pipeline_id is not None or table_group is not None:
        return table_names_to_delete


@app.route('/data/<table>', methods=['GET'])
def data(table):
    args = request.args
        
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Format query based on args
    query_limit = ''
    query_timestamp_where = ''
    query_row_number_select = ''
    query_row_number_where = ''
    
    if args.get('start') is None or args.get('end') is None:
        query_limit = 'LIMIT 10000'
    else:
        query_timestamp_where = f'''
            WHERE
                timestamp >= {args.get('start')}
                AND timestamp < {args.get('end')}
        '''

    if args.get('aggregate') is not None and args.get('aggregate'):
        query_row_number_select = '''
            , ROW_NUMBER() OVER (
                PARTITION BY candle_timestamp
                ORDER BY timestamp DESC
            ) AS row_number
        '''
        query_row_number_where = 'WHERE row_number = 1'

    # Select columns
    cur.execute(f'''
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table}'
    ''')
    column_results = cur.fetchall()
    column_names = []
    time_indices = []  # store time indices for time formatting
    for i in range(len(column_results)):
        column_name = column_results[i][0]
        column_names.append(column_name)
        if re.search('timestamp', column_name) is not None:
            time_indices.append(i)

    QUERY = f'''
        SELECT {','.join(column_names)}
        FROM (
            SELECT
                *
                {query_row_number_select}
            FROM {table}
            {query_timestamp_where}
        ) AS data
        {query_row_number_where}
        ORDER BY timestamp
        {query_limit}
    '''
    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Format timestamps if required
    if args.get('time_format') is not None and args.get('time_format') == 'datetime':
        formatted_query_result = []
        for row in query_result:
            formatted_row = list(row)
            for i in time_indices:
                try:
                    formatted_row[i] = timestamp_to_date(formatted_row[i] / 1000) if formatted_row[i] > 0 else formatted_row[i]
                except:
                    pass
            formatted_query_result.append(formatted_row)
        query_result = formatted_query_result
    
    # Format output as dicts
    if args.get('data_format') is not None and args.get('data_format') == 'dict':
        formatted_query_result = []
        for row in query_result:
            formatted_row = collections.OrderedDict()
            for column_name, value in zip(column_names, row):
                formatted_row[column_name] = value
            formatted_query_result.append(formatted_row)
        query_result = formatted_query_result
        
    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/datarange', methods=['GET'])
def datarange():
    args = request.args
    table_name = args.get('table')

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    cur.execute(f'''
        SELECT
            COALESCE(MIN(timestamp), 0) AS min_timestamp
            , COALESCE(MAX(timestamp), 0) AS max_timestamp
        FROM {table_name}
    ''')
    query_result = cur.fetchall()

    # Format timestamps if required
    if args.get('time_format') is not None and args.get('time_format') == 'datetime':
        formatted_query_result = []
        for row in query_result:
            formatted_row = list(row)
            for i in range(len(formatted_row)):
                formatted_row[i] = timestamp_to_date(formatted_row[i] / 1000) if formatted_row[i] > 0 else formatted_row[i]
            formatted_query_result.append(formatted_row)
        query_result = formatted_query_result

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()

    return {'data': query_result[0]}


@app.route('/create_table', methods=['POST'])
def create_table():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Parse json data
    data = request.get_json()

    # Create a table
    cur.execute(f'''
        DROP TABLE IF EXISTS {data['table']};
        CREATE TABLE {data['table']} ({','.join(data['schema'])});
    ''')

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()

    return f'Table \'{data["table"]}\' has been created'

@app.route('/insert', methods=['POST'])
def insert():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Parse json data
    data = request.get_json()

    # Insert values into table
    cur.execute(f'''
        INSERT INTO {data['table']}
        VALUES {','.join(data['values'])};
    ''')

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()

    return 'Values inserted'

@app.route('/charts/candles', methods=['GET'])
def chart_candles():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , open
            , close
            , high
            , low
            , is_complete
        FROM {args.get('symbol')}_candles_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/highs', methods=['GET'])
def chart_highs():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , high_timestamp_history
            , is_complete
        FROM {args.get('symbol')}_high_low_history_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/lows', methods=['GET'])
def chart_lows():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , low_timestamp_history
            , is_complete
        FROM {args.get('symbol')}_high_low_history_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/resistance', methods=['GET'])
def chart_resistance():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , top_history
            , is_complete
        FROM {args.get('symbol')}_resistance_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/support', methods=['GET'])
def chart_support():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , bottom_history
            , is_complete
        FROM {args.get('symbol')}_support_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/rsi', methods=['GET'])
def chart_rsi():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , rsi
            , is_complete
        FROM {args.get('symbol')}_rsi_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/retracement', methods=['GET'])
def chart_retracement():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , high_retracement
            , low_retracement
            , is_complete
        FROM {args.get('symbol')}_retracement_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/avg_rsi', methods=['GET'])
def chart_avg_rsi():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , avg_rsi
            , is_complete
        FROM {args.get('symbol')}_avg_rsi_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/aggregate_retracement_long', methods=['GET'])
def chart_aggregate_retracement_long():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , agg_retracement_long
            , is_complete
        FROM {args.get('symbol')}_aggregate_retracement_long_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/retracement_long', methods=['GET'])
def chart_retracement_long():
    # Require args
    args = request.args
    required_args = ['symbol', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , retracement_timeframe
            , high_retracement
            , oversold_timeframe
            , avg_rsi
        FROM {args.get('symbol')}_retracement_long_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/trader', methods=['GET'])
def chart_trader():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        WITH
        trader AS (
            SELECT
                timestamp
                , equity
            FROM trader_{args.get('pipeline_id')}
            WHERE
                timestamp >= {args.get('start')}
                AND timestamp < {args.get('end')}
        )
        
        , candles AS (
            SELECT
                timestamp
                , candle_timestamp
                , is_complete
            FROM {args.get('symbol')}_candles_{args.get('timeframe')}_{args.get('pipeline_id')}
            WHERE
                timestamp >= {args.get('start')}
                AND timestamp < {args.get('end')}
        )

        SELECT
            timestamp
            , candles.candle_timestamp
            , trader.equity
            , candles.is_complete
        FROM trader
        INNER JOIN candles
            USING ( timestamp )
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/aggregate_buy_sell', methods=['GET'])
def chart_aggregate_buy_sell():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , agg_buy
            , agg_sell
            , is_complete
        FROM {args.get('symbol')}_aggregate_buy_sell_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/risk', methods=['GET'])
def chart_risk():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , recent_sup_top
            , recent_sup_bottom
            , risk
        FROM trader_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/structure', methods=['GET'])
def chart_structure():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , struct_top
            , equil_top
            , struct_bottom
            , equil_bottom
            , is_complete
        FROM {args.get('symbol')}_structure_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

@app.route('/charts/rsi_projection', methods=['GET'])
def chart_rsi_projection():
    # Require args
    args = request.args
    required_args = ['symbol', 'timeframe', 'pipeline_id', 'start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None:
            missing_args.append(required_arg)
    if len(missing_args) > 0:
        return {'error': 'Missing parameters: ' + str(missing_args)}, 400

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Fetch data from table
    QUERY = f'''
        SELECT
            timestamp
            , candle_timestamp
            , price_projection
            , is_complete
        FROM {args.get('symbol')}_rsi_projection_{args.get('timeframe')}_{args.get('pipeline_id')}
        WHERE
            timestamp >= {args.get('start')}
            AND timestamp < {args.get('end')}
        ORDER BY timestamp
    '''

    cur.execute(QUERY)
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()
    return {'data': query_result}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4500, debug=True)
