from .production import *


STATIC_URL = os.environ['STATIC_URL']

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

ADMINS = [('Matus Zelenak', 'matus.zelenak@trojsten.com')]
