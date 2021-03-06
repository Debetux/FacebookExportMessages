from flask import flash, redirect, request, render_template, url_for, session, escape, session, make_response
import json
import requests
import urllib.request
import datetime
import time
import os
import tasks
from settings import *

from app import app
from models import User


@app.template_filter('strftime')
def _jinja2_filter_datetime(date_arg, fmt=None):
    date = datetime.datetime.strptime(date_arg, '%Y-%m-%dT%X%z')
    # date = datetime.datetime(date_arg)
    return date.strftime('%b %d %Y %H:%M:%S')


@app.route('/', methods=['GET', 'POST'])
def home():

    logged_in = False
    inbox = None

    if 'fb_user' in session:
        access_token = session['access_token']
        logged_in = True

        inbox = requests.get(
            'https://graph.facebook.com/me/inbox',
            params={
                'access_token': access_token
            }
        )

        if inbox.status_code == requests.codes.ok:
            inbox = inbox.json()

    return render_template('index.html', session=session, threads=inbox, logged_in=logged_in)


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

    if 'fb_user' in session:
        access_token = session['access_token']
        tasks.generate_csv.delay(access_token, session['email'], thread_id)

    return render_template('pending.html')


@app.route('/download/<thread_id>.csv', methods=['GET', 'POST'])
def download_thread_csv(thread_id):
    file = open('data/{}.csv'.format(thread_id), 'r')
    csv = file.read()
    # We need to modify the response, so the first thing we 
    # need to do is create a response out of the CSV string
    response = make_response(csv)
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename={}.csv".format(thread_id)
    file.close()

    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    verification_code = request.args.get("code")

    """ Auth with Facebook is very simple. """
    args = dict(client_id=FACEBOOK_APP_ID,
                redirect_uri=url_for('login', _external=True), scope="read_mailbox, email")

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
        session['fb_name'] = str(profile["name"])
        session['email'] = str(profile["email"])
        session['access_token'] = access_token

        try:
            with db.atomic():
                user = User.create(facebook_id = profile["id"], facebook_email = profile["email"], facebook_name = profile["name"])

        except peewee.IntegrityError:
            user = User.get(User.facebook_id == profile["id"])

        return redirect("/")
    else:
        return redirect(
            "https://graph.facebook.com/oauth/authorize?" +
            urllib.parse.urlencode(args))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('fb_user', None)
    session.pop('fb_name', None)
    session.pop('email', None)
    session.pop('access_token', None)
    return redirect(url_for('home'))
