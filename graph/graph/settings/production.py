import dj_database_url

from .base import *

DEBUG = False

PRODUCTION = True

ALLOWED_HOSTS += ['trojsten-graph.herokuapp.com']

DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
