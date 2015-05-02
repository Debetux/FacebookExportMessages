from celery import Celery
from settings import CELERY_RESULT_BACKEND, BROKER_URL, POSTMARK_API_TOKEN, POSTMARK_SENDER
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
                     sender=POSTMARK_SENDER,
                     to="debetux@gmail.com",
                     text_body="Hello {}".format(x + y),
                     tag="hello")

    message.send()
    return x + y


@app.task
def generate_csv(access_token, thread_id):
    import csv
    import json
    import urllib
    import time
    import base64

    """ Prepare file """
    file = open('data/{}.csv'.format(thread_id), 'w', newline='')
    csvfile = csv.writer(file)

    request = json.loads(urllib.request.urlopen( "https://graph.facebook.com/{}/comments?".format(thread_id) + urllib.parse.urlencode(dict(access_token=access_token, limit=30))).read().decode('utf-8'))
    msg_count = 0
    reqs = 0

    # if request['data'] is empty, there isn't more data to retrieve via the API.
    while len(request['data']) > 0:
        reqs += 1
        time.sleep(1.1)

        for message in reversed(request['data']):
            if 'message' in message:
                csvfile.writerow([ message['from']['name'].encode('utf-8'), message['created_time'].encode('utf-8'), message['message'].encode('utf-8')])
            else:
                csvfile.writerow([ message['from']['name'].encode('utf-8'), message['created_time'].encode('utf-8'), ""])
            msg_count += 1

        if request['paging']['next']:
            tried = 0
            while True:
                tried += 1
                try:
                    request_new = json.loads(urllib.request.urlopen( request['paging']['next']).read().decode('utf-8'))
                except urllib.error.HTTPError as e:
                    print(e)
                    print('URL :', request['paging']['next'])
                    time.sleep(tried*80)
                    continue
                break

            request = None
            request = request_new

        # file.seek(0)

    file.close()
    print('Message count :', msg_count)
    print('Number of request :', reqs)
    data = open('data/{}.csv'.format(thread_id), 'rb').read()
    encoded = base64.b64encode(data)

    message = PMMail(api_key=POSTMARK_API_TOKEN,
                     subject="CSV Generated for {}".format(thread_id),
                     sender=POSTMARK_SENDER,
                     to="debetux@gmail.com",
                     text_body="Hello, {} messages for {} requests".format(msg_count, reqs),
                     tag="hello",
                     attachments=[
                        ('history.csv', encoded,'application/octet-stream')
                     ])

    message.send()
