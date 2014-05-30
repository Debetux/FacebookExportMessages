from flask import Flask, flash, redirect, request, render_template, url_for, session, escape, session
import json
import requests
import urllib
import datetime
import time



FACEBOOK_APP_ID = ""
FACEBOOK_APP_SECRET = ""
SECRET_KEY = "DZDZ"

app = Flask(__name__)
app.config.from_object(__name__)

@app.template_filter('strftime')
def _jinja2_filter_datetime(date_arg, fmt=None):
    date = datetime.datetime.strptime(date_arg, '%Y-%m-%dT%X%z')
    # date = datetime.datetime(date_arg)
    return date.strftime('%b %d %Y %H:%M:%S')

@app.route('/', methods=['GET', 'POST'])
def home():

    logged_in = False
    hop = None
    if 'fb_user' in session:
        access_token = session['access_token']
        logged_in = True

        try:
            hop = json.loads(urllib.request.urlopen( "https://graph.facebook.com/me/inbox?" + urllib.parse.urlencode(dict(access_token=access_token))).read().decode('utf-8'))
            # hop = json.dumps(hop, indent=4, sort_keys=True)
            # print(hop)

        except urllib.error.HTTPError as e:
            hop = "https://graph.facebook.com/me/inbox?" + urllib.parse.urlencode(dict(access_token=access_token))


    return render_template('index.html', session = session, hop = hop, threads = hop, logged_in = logged_in)

@app.route('/thread/<thread_id>', methods=['GET', 'POST'])
def view_thread(thread_id):

    logged_in = False
    if 'fb_user' in session:
        access_token = session['access_token']
        logged_in = True

        try:
            hop = json.loads(urllib.request.urlopen( "https://graph.facebook.com/{}?".format(thread_id) + urllib.parse.urlencode(dict(access_token=access_token))).read().decode('utf-8'))

        except urllib.error.HTTPError as e:
            hop = "https://graph.facebook.com/me/inbox?" + urllib.parse.urlencode(dict(access_token=access_token))


    return render_template('thread.html', session = session, hop = hop, threads = hop, logged_in = logged_in)


@app.route('/download/<thread_id>', methods=['GET', 'POST'])
def download_thread(thread_id):
    import csv

    logged_in = False
    if 'fb_user' in session:
        access_token = session['access_token']
        logged_in = True

        """ Prepare file """
        file = open('data/{}.csv'.format(thread_id), 'w', newline='')
        csvfile = csv.writer(file)
        
        request = json.loads(urllib.request.urlopen( "https://graph.facebook.com/{}/comments?".format(thread_id) + urllib.parse.urlencode(dict(access_token=access_token, limit=30))).read().decode('utf-8'))
        msg_count = 0
        reqs = 0

        while len(request['data']) > 0:
            reqs += 1
            time.sleep(1.1)

            for message in reversed(request['data']):
                if 'message' in message:
                    # print(message['message'].encode('utf-8'))

#                     file.write("""
# \n
#                     """.format(name = message['from']['name'].encode('utf-8'), date = message['created_time'].encode('utf-8'), message = message['message'].encode('utf-8') ))
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
        print(msg_count)
        print(reqs)

    return render_template('downloaded.html', endr = request)





@app.route('/login', methods=['GET', 'POST'])
def login():
    verification_code = request.args.get("code")

    args = dict(client_id=FACEBOOK_APP_ID,
                redirect_uri=url_for('login', _external=True), scope="read_mailbox")

    if request.args.get("code"):
        args["client_secret"] = FACEBOOK_APP_SECRET
        args["code"] = request.args.get("code")
        response = urllib.parse.parse_qs(urllib.request.urlopen(
            "https://graph.facebook.com/oauth/access_token?" +
            urllib.parse.urlencode(args)).read().decode('utf-8'))
            
        access_token = response['access_token'][-1]

        # Download the user profile and cache a local instance of the
        # basic profile info
        profile = json.loads(
            urllib.request.urlopen( "https://graph.facebook.com/me?" + urllib.parse.urlencode(dict(access_token=access_token))).read().decode('utf-8') )

        session['fb_user'] = str(profile["id"])
        session['access_token'] = access_token
        return redirect("/")
    else:
        return redirect(
            "https://graph.facebook.com/oauth/authorize?" +
            urllib.parse.urlencode(args))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8801, debug=True)

