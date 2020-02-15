from .production import *

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

PARENT_HOST = 'graph.trojsten.wtf'

STATIC_URL = os.environ['STATIC_URL']

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

ADMINS = [('Matus Zelenak', 'matus.zelenak@trojsten.com')]
