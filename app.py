from flask import Flask
import os

from settings import *
from peewee import SqliteDatabase

APP_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(APP_ROOT, 'app.db')

app = Flask(__name__)
app.config.from_object(__name__)
db = SqliteDatabase(app.config['DATABASE'], threadlocals=True)
