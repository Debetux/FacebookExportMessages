import os

FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
SECRET_KEY = os.environ.get('SECRET_KEY')
BROKER_URL = os.environ.get('BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_SENDER = os.environ.get('MAILGUN_SENDER')
