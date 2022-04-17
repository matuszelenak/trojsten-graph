from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = False

PRODUCTION = True

HOST_SCHEME = 'https://'

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'api.utils.sentry_capture_exception_handler'
