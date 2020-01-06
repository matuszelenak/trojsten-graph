from .base import *

DEBUG = True

PRODUCTION = False

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


INTERNAL_IPS = [
    '127.0.0.1',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

INSTALLED_APPS += ['debug_toolbar']
