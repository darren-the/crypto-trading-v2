from flask import Flask
from flask_cors import CORS
from pipeline.pipeline import run_pipeline
from celery import Celery, Task

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

app = Flask(__name__)
app.config.from_mapping(
    CELERY=dict(
        broker_url='redis://localhost',
        result_backend='redis://localhost',
        task_ignore_result=True,
    ),
)
celery_app = celery_init_app(app)
CORS(app)

@app.route('/run', methods=['GET'])
def run():
    run_pipeline()
    
    return {'status': 'pipeline has finished'}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)
