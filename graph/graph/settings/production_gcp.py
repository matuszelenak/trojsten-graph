from .production import *

DEBUG = False

PRODUCTION = True


ALLOWED_HOSTS = [
    'trojsten-graph.appspot.com',
    '127.0.0.1',
    'localhost'
]

STATIC_URL = os.environ['STATIC_URL']

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

ADMINS = [('Matus Zelenak', 'matus.zelenak@trojsten.com')]
