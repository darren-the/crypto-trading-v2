from celery import shared_task
import celery

@shared_task
def add_together(a, b):
    return a + b