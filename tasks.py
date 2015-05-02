from celery import Celery
from settings import CELERY_RESULT_BACKEND, BROKER_URL, MAILGUN_API_KEY, MAILGUN_SENDER
import requests

app = Celery('example')
app.conf.update(BROKER_URL=BROKER_URL,
                CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND,
                CELERY_TASK_SERIALIZER='json',
                CELERY_ACCEPT_CONTENT=['json'])


@app.task
def add(x, y):
    return x + y


@app.task
def generate_csv(access_token, thread_id):
    import csv
    import json
    import urllib.request
    import time
    # import tarfile

    """ Prepare file """
    file = open('data/{}.csv'.format(thread_id), 'w')
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
                    time.sleep(tried * 80)
                    continue
                break

            request = None
            request = request_new

        # file.seek(0)

    file.close()

    # tar = tarfile.open("data/{}.tar.gz".format(thread_id), "w:gz")
    # tar.add('data/{}.csv'.format(thread_id))
    # tar.close()

    print('Message count :', msg_count)
    print('Number of request :', reqs)

    requests.post(
        "https://api.mailgun.net/v3/app80543588b752474a9dcfdb06376844b4.mailgun.org/messages",
        auth=("api", MAILGUN_API_KEY),
        files=[("history.csv", open('data/{}.csv'.format(thread_id)))],
        data={
            "from": "Excited User <app36434178@heroku.com>",
            "to": "debetux@gmail.com",
            "subject": "Hello",
            "text": "Hello, {} messages for {} requests".format(msg_count, reqs),
            "html": "Hello, {} messages for {} requests".format(msg_count, reqs)
        }
    )
    return 'Done'
