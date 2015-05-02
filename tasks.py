from celery import Celery
from settings import CELERY_RESULT_BACKEND, BROKER_URL, POSTMARK_API_TOKEN, POSTMARK_SENDER
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

app = Celery('example')
app.conf.update(BROKER_URL=BROKER_URL,
                CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND,
                CELERY_TASK_SERIALIZER='json',
                CELERY_ACCEPT_CONTENT=['json'])


@app.task
def add(x, y):
    return x + y


def send_mail(send_from, send_to, subject, text, files=None,
              server="127.0.0.1"):
    assert isinstance(send_to, list)

    msg = MIMEMultipart(
        From=send_from,
        To=COMMASPACE.join(send_to),
        Date=formatdate(localtime=True),
        Subject=subject
    )
    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            msg.attach(MIMEApplication(
                fil.read(),
                Content_Disposition='attachment; filename="%s"' % basename(f)
            ))

    smtp = smtplib.SMTP(server)
    smtp.login(POSTMARK_API_TOKEN, POSTMARK_API_TOKEN)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()


@app.task
def generate_csv(access_token, thread_id):
    import csv
    import json
    import urllib.request
    import time
    import base64

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
    print('Message count :', msg_count)
    print('Number of request :', reqs)
    send_mail(
        POSTMARK_SENDER,
        ['debetux@gmail.com'],
        'FacebookExportMessages', "Hello, {} messages for {} requests".format(msg_count, reqs),
        ['data/{}.csv'.format(thread_id)],
        'smtp.postmarkapp.com'
    )
    return 'Done'
