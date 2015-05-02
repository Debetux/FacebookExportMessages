from celery import Celery
from settings import CELERY_RESULT_BACKEND, BROKER_URL, MANDRILL_APIKEY
import mandrill

app = Celery('example')
app.conf.update(BROKER_URL=BROKER_URL,
                CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND,
                CELERY_TASK_SERIALIZER='json',
                CELERY_ACCEPT_CONTENT=['json'])


def send_mail(email_to, message):
    mandrill_client = mandrill.Mandrill(MANDRILL_APIKEY)
    message = {
        'to': [],
        'global_merge_vars': []
    }
    for em in email_to:
        message['to'].append({'email': em})

    mandrill_client.messages.send(message=message)


@app.task
def add(x, y):
    send_mail(['debetux@gmail.com'], 'email test: {}'.format(x + y))
    return x + y
