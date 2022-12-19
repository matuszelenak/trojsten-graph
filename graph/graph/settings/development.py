from .base import *

DEBUG = True

PRODUCTION = False

INTERNAL_IPS = [
    '127.0.0.1',
]

# INSTALLED_APPS += ['debug_toolbar']
#
# MIDDLEWARE = [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ] + MIDDLEWARE

SESSION_COOKIE_SECURE = False

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
