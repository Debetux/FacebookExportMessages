import datetime

from peewee import *
from app import db


class User(Model):
    facebook_id = CharField(unique=True)
    facebook_name = CharField()
    facebook_email = CharField()

    class Meta:
        database = db


class Conversation(Model):
    user = ForeignKeyField(User, related_name='conversations')
    facebook_id = CharField(unique=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class Message(Model):
    conversation = ForeignKeyField(Conversation, related_name='conversations')
    facebook_id = CharField(unique=True)
    from_facebook_id = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
