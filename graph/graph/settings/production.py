from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = False

PRODUCTION = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    f'https://{origin}'
    for origin in os.environ.get("ALLOWED_HOSTS").split(" ")
]

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'api.utils.sentry_capture_exception_handler'
