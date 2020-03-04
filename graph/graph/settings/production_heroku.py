import dj_database_url

from .production import *

PARENT_HOST = 'graph.trojsten.wtf'

# MIDDLEWARE = list(MIDDLEWARE)
# MIDDLEWARE.remove('django_hosts.middleware.HostsRequestMiddleware')
# MIDDLEWARE = tuple(MIDDLEWARE)
#
# MIDDLEWARE = (
#     'django_hosts.middleware.HostsRequestMiddleware',
#     'whitenoise.middleware.WhiteNoiseMiddleware',
# ) + MIDDLEWARE
#
# INSTALLED_APPS += ['whitenoise']
#
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ADMINS = [('Matus Zelenak', 'matus.zelenak@trojsten.com')]

DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}
