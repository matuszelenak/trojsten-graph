import dj_database_url

from .production import *

MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.remove('django_hosts.middleware.HostsRequestMiddleware')
MIDDLEWARE = tuple(MIDDLEWARE)

MIDDLEWARE = (
    'django_hosts.middleware.HostsRequestMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
) + MIDDLEWARE

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600

CORS_ALLOWED_ORIGINS = [
    "https://graph.trihedron.wtf",
    "https://www.graph.trihedron.wtf",
]

CSRF_TRUSTED_ORIGINS = [
    'https://graph.trihedron.wtf',
    'https://www.graph.trihedron.wtf',
]
