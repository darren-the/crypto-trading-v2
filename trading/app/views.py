from flask import Blueprint
from app.tasks import run_pipeline
from celery.result import AsyncResult


main = Blueprint('main', __name__)
pipeline_id = None

@main.route('/run', methods=['GET'])
def run():
    global pipeline_id
    if pipeline_id is None:
        result = run_pipeline.delay()
        pipeline_id = result.id
        return 'pipeline has started.'
    else:
        return 'pipeline job has already been started.'

@main.route('/status', methods=['GET'])
def task_result():
    if pipeline_id is not None:
        result = AsyncResult(pipeline_id)
        return {
            'ready': result.ready(),
            'successful': result.successful(),
            'value': 
            result.result if result.ready() else None,
        }
    else:
        return 'pipeline is not running.'
    