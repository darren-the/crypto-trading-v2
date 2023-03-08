from celery import shared_task
from pipeline.pipeline import run


@shared_task
def run_pipeline(pipeline_id):
    run(pipeline_id)
    return True
