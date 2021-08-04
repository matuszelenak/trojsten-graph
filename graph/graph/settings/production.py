from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = False

PRODUCTION = True

HOST_SCHEME = 'https://'

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
