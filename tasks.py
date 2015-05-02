from celery import Celery
from settings import CELERY_RESULT_BACKEND, BROKER_URL

app = Celery('example')

app.conf.update(BROKER_URL=BROKER_URL,
                CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND,
                CELERY_TASK_SERIALIZER='json')


@app.task
def add(x, y):
    return x + y
