from flask import Flask
from flask_cors import CORS
from pipeline.pipeline import run_pipeline
import os

app = Flask(__name__)
CORS(app)


@app.route('/run', methods=['GET'])
def run():
    run_pipeline()
    
    return {'status': 'pipeline has finished'}

@app.route('/test', methods=['GET'])
def test():
    return 'hello world'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)
