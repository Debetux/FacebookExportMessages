from celery import Celery
from settings import CELERY_RESULT_BACKEND, BROKER_URL
import mandrill

app = Celery('example')
app.conf.update(BROKER_URL=BROKER_URL,
                CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND,
                CELERY_TASK_SERIALIZER='json',
                CELERY_ACCEPT_CONTENT=['json'])

mandrill_client = mandrill.Mandrill(MANDRILL_APIKEY)


@app.task
def add(x, y):
    return x + y
