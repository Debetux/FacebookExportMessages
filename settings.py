import os
import glob
import sys

if 'test' in sys.argv:
    env_dir = os.path.join('tests', 'envdir')
else:
    env_dir = 'envdir'
env_vars = glob.glob(os.path.join(env_dir, '*'))
for env_var in env_vars:
    with open(env_var, 'r') as env_var_file:
        os.environ.setdefault(env_var.split(os.sep)[-1],
                              env_var_file.read().strip())

FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
SECRET_KEY = os.environ.get('SECRET_KEY')
BROKER_URL = os.environ.get('BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_SENDER = os.environ.get('MAILGUN_SENDER')
DATABASE_URL = os.environ.get('DATABASE_URL')
