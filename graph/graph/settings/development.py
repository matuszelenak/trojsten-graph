from .base import *

DEBUG = True

PRODUCTION = False

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'graph',
        'USER': 'graph',
        'HOST': os.environ.get('PGHOST', 'localhost'),
        'PORT': 5432
    }
}
