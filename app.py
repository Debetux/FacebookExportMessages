from flask import Flask
import os
import urllib.parse

from settings import *
from peewee import PostgresqlDatabase

APP_ROOT = os.path.dirname(os.path.realpath(__file__))
urllib.parse.uses_netloc.append('postgres')
DATABASE = urllib.parse.urlparse(DATABASE_URL)

app = Flask(__name__)
app.config.from_object(__name__)
db = PostgresqlDatabase(DATABASE.path[1:], user=DATABASE.username, host=DATABASE.hostname, port=DATABASE.port)
