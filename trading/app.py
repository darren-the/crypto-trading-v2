from flask import Flask
from flask_cors import CORS
# from pipeline.pipeline import run_pipeline
from celery import Celery, Task, shared_task
from celery.result import AsyncResult


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)
    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.conf.update(
        imports=['app.add_together']
    )
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

app = Flask(__name__)
app.config.from_mapping(
    CELERY=dict(
        broker_url='redis://redis:6379',
        result_backend='redis://redis:6379',
        task_ignore_result=True,
    ),
)
celery_app = celery_init_app(app)
CORS(app)

@celery_app.task
def add_together(a, b):
    return a + b

@app.route('/run', methods=['GET'])
def run():
    result = add_together.delay(10, 25)
    return {'result_id': result.id}

@app.route("/result/<id>", methods=['GET'])
def task_result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    return {
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if result.ready() else None,
    }


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)
