from .base import *

DEBUG = True

PRODUCTION = False

INTERNAL_IPS = [
    '127.0.0.1',
]

MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.remove('django_hosts.middleware.HostsRequestMiddleware')
MIDDLEWARE = tuple(MIDDLEWARE)

MIDDLEWARE = (
    'django_hosts.middleware.HostsRequestMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE

# INSTALLED_APPS += ['debug_toolbar']

SESSION_COOKIE_SECURE = False

SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS = ['localhost:8000', 'localhost:3000']

import mimetypes

mimetypes.add_type("application/javascript", ".js", True)

DEBUG_TOOLBAR_PATCH_SETTINGS = False


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    'INSERT_BEFORE': '</head>',
    'INTERCEPT_REDIRECTS': False,
    'RENDER_PANELS': True,
}
