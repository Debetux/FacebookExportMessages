from celery import Celery
from settings import CELERY_RESULT_BACKEND, BROKER_URL, POSTMARK_API_TOKEN
from postmark import PMMail

app = Celery('example')
app.conf.update(BROKER_URL=BROKER_URL,
                CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND,
                CELERY_TASK_SERIALIZER='json',
                CELERY_ACCEPT_CONTENT=['json'])


@app.task
def add(x, y):
    message = PMMail(api_key=POSTMARK_API_TOKEN,
                     subject="Hello from Postmark",
                     sender="leonard@bigbangtheory.com",
                     to="debetux@gmail.com",
                     text_body="Hello {}".format(x + y),
                     tag="hello")

    message.send()
    return x + y
