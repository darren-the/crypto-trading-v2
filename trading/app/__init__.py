
from flask import Flask
from app.views import main
from app.utils import make_celery


app = Flask(__name__)
app.config["CELERY_CONFIG"] = {
    "broker_url": "redis://redis",
    "result_backend": "redis://redis"
}

celery = make_celery(app)
celery.set_default()

app.register_blueprint(main)
