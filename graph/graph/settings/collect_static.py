from django.contrib.staticfiles.apps import StaticFilesConfig

from .development import *


class GraphStaticConfig(StaticFilesConfig):
    ignore_patterns = [
        '*.sh', 'node_modules', '*.json',
    ]


INSTALLED_APPS.remove('django.contrib.staticfiles')
INSTALLED_APPS.append('graph.settings.collect_static.GraphStaticConfig')
