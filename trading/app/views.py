from flask import Blueprint
from app.tasks import run_pipeline
from celery.result import AsyncResult


main = Blueprint('main', __name__)
result_id = None

@main.route('/run/<pipeline_id>', methods=['GET'])
def run(pipeline_id):
    global result_id
    if result_id is None:
        result = run_pipeline.delay(pipeline_id)
        result_id = result.id
        return 'pipeline has started.'
    else:
        return 'pipeline job has already been started.'

@main.route('/status', methods=['GET'])
def task_result():
    if result_id is not None:
        result = AsyncResult(result_id)
        return {
            'ready': result.ready(),
            'successful': result.successful(),
            'value': 
            result.result if result.ready() else None,
        }
    else:
        return 'pipeline is not running.'
    