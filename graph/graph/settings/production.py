from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = False

PRODUCTION = True

HOST_SCHEME = 'https://'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CORS_ALLOWED_ORIGINS = [
    "https://graph.trihedron.wtf",
    "https://www.graph.trihedron.wtf",
]

CSRF_TRUSTED_ORIGINS = [
    'https://graph.trihedron.wtf',
    'https://www.graph.trihedron.wtf',
]

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'api.utils.sentry_capture_exception_handler'
