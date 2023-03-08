from flask import Flask, request
from flask_cors import CORS
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
from decimal import Decimal

app = Flask(__name__)
CORS(app)

DEC2FLOAT = psycopg2.extensions.new_type(
psycopg2.extensions.DECIMAL.values,
'DEC2FLOAT',
lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)

@app.route('/postgresql_test', methods=['GET'])
def postgresql_test():
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name FROM information_schema.tables
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

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="db",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Delete table(s)
    if pipeline_id is None:
        cur.execute(f'DROP TABLE IF EXISTS {table_name};')
    else:
        cur.execute(f'''
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name LIKE '%{pipeline_id}';
        ''')
        table_names_to_delete = cur.fetchall()
        for table in table_names_to_delete:
            cur.execute(f'DROP TABLE IF EXISTS {table[0]}')

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()

    if pipeline_id is None:
        return f'Table \'{table_name}\' has been deleted'
    else:
        return table_names_to_delete


@app.route('/data/<table>', methods=['GET'])
def data(table):
    # Require args
    args = request.args
    required_args = ['start', 'end']
    missing_args = []
    for required_arg in required_args:
        if args.get(required_arg) is None and not \
            (required_arg == 'timeframe' and table[7:].lower() == 'base_candles'):  # exception for base candles
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
        SELECT *
        FROM {table}
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
            COALESCE(MIN(timestamp), 0)
            , COALESCE(MAX(timestamp), 0)
        FROM {table_name}
    ''')
    query_result = cur.fetchall()

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
            candle_timestamp
            , open
            , close
            , high
            , low
        FROM (
            SELECT
                *
                , ROW_NUMBER() OVER (
                    PARTITION BY candle_timestamp
                    ORDER BY timestamp DESC
                ) AS row_number
            FROM {args.get('symbol')}_candles_{args.get('timeframe')}_{args.get('pipeline_id')}
            WHERE
                candle_timestamp >= {args.get('start')}
                AND candle_timestamp < {args.get('end')}
        ) AS candles
        WHERE row_number = 1 
        ORDER BY candle_timestamp
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
        SELECT high_timestamp
        FROM (
            SELECT
                high_timestamp
                , candle_timestamp
                , ROW_NUMBER() OVER (
                    PARTITION BY candle_timestamp
                    ORDER BY timestamp DESC
                ) AS row_number
            FROM {args.get('symbol')}_high_low_{args.get('timeframe')}_{args.get('pipeline_id')}
            WHERE
                candle_timestamp >= {args.get('start')}
                AND candle_timestamp < {args.get('end')}
                AND is_high = TRUE
        ) AS highs
        WHERE row_number = 1 
        ORDER BY candle_timestamp
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
        SELECT low_timestamp
        FROM (
            SELECT
                low_timestamp
                , candle_timestamp
                , ROW_NUMBER() OVER (
                    PARTITION BY candle_timestamp
                    ORDER BY timestamp DESC
                ) AS row_number
            FROM {args.get('symbol')}_high_low_{args.get('timeframe')}_{args.get('pipeline_id')}
            WHERE
                candle_timestamp >= {args.get('start')}
                AND candle_timestamp < {args.get('end')}
                AND is_low = TRUE
        ) AS lows
        WHERE row_number = 1 
        ORDER BY candle_timestamp
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
            candle_timestamp
            , top_history
        FROM (
            SELECT
                candle_timestamp
                , top_history
                , ROW_NUMBER() OVER (
                    PARTITION BY candle_timestamp
                    ORDER BY timestamp DESC
                ) AS row_number
            FROM {args.get('symbol')}_resistance_{args.get('timeframe')}_{args.get('pipeline_id')}
            WHERE
                candle_timestamp >= {args.get('start')}
                AND candle_timestamp < {args.get('end')}
        ) AS resistance
        WHERE row_number = 1 
        ORDER BY candle_timestamp
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
            candle_timestamp
            , bottom_history
        FROM (
            SELECT
                candle_timestamp
                , bottom_history
                , ROW_NUMBER() OVER (
                    PARTITION BY candle_timestamp
                    ORDER BY timestamp DESC
                ) AS row_number
            FROM {args.get('symbol')}_support_{args.get('timeframe')}_{args.get('pipeline_id')}
            WHERE
                candle_timestamp >= {args.get('start')}
                AND candle_timestamp < {args.get('end')}
        ) AS support
        WHERE row_number = 1 
        ORDER BY candle_timestamp
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
            candle_timestamp
            , rsi
        FROM (
            SELECT
                candle_timestamp
                , rsi
                , ROW_NUMBER() OVER (
                    PARTITION BY candle_timestamp
                    ORDER BY timestamp DESC
                ) AS row_number
            FROM {args.get('symbol')}_rsi_{args.get('timeframe')}_{args.get('pipeline_id')}
            WHERE
                candle_timestamp >= {args.get('start')}
                AND candle_timestamp < {args.get('end')}
        ) AS rsi
        WHERE row_number = 1 
        ORDER BY candle_timestamp
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
