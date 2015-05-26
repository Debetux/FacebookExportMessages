from flask import Flask, flash, redirect, request, render_template, url_for, session, escape, session, make_response
import json
import requests
import urllib.request
import datetime
import time
import os
import tasks
from settings import *
from peewee import SqliteDatabase

APP_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(APP_ROOT, 'notes.db')

app = Flask(__name__)
app.config.from_object(__name__)
db = SqliteDatabase(app.config['DATABASE'], threadlocals=True)
