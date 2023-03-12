from flask import Flask, request
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)


@app.route('/pipeline/create_table', methods=['POST'])
def create_table():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="172.18.0.3",
        database="mydatabase",
        user="myuser",
        password="mypassword"
    )
    cur = conn.cursor()

    # Parse json data
    result = request.get_json()
    print(result)

    # Create a table
    # cur.execute(f"""
    #     DROP TABLE IF EXISTS base_candles;
    #     CREATE TABLE base_candles (
    #         timestamp NUMERIC PRIMARY KEY,
    #         open NUMERIC NOT NULL,
    #         close NUMERIC NOT NULL,
    #         high NUMERIC NOT NULL,
    #         low NUMERIC NOT NULL
    #     );
    # """)

    # cur.execute("""
    #     SELECT table_name FROM information_schema.tables
    # """)

    # x = cur.fetchall()
    # print(x)    

    
    # # Commit the transaction
    # conn.commit()

    cur.close()
    conn.close()

    return 'hi'

@app.route('/test', methods=['GET'])
def test():
    return 'test succeeded!'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4500, debug=True)
