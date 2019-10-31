import dj_database_url

from .base import *

DEBUG = False

PRODUCTION = True

ALLOWED_HOSTS += ['trojsten-graph.herokuapp.com']

DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
