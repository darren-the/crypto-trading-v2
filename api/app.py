from flask import Flask, request
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)


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


@app.route('/data/<table>', methods=['GET'])
def data(table):
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
        SELECT MIN(timestamp), MAX(timestamp)
        FROM {table}
    ''')
    query_result = cur.fetchall()

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()

    return {'data': query_result}


@app.route('/pipeline/create_table', methods=['POST'])
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

@app.route('/pipeline/insert', methods=['POST'])
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4500, debug=True)
