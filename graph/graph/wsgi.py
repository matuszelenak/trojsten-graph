"""
WSGI config for graph project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graph.settings')

_application = get_wsgi_application()


def application(environ, start_response):
    script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
    if script_name:
        environ['SCRIPT_NAME'] = script_name
        path_info = environ['PATH_INFO']
        if path_info.startswith(script_name):
            environ['PATH_INFO'] = path_info[len(script_name):]

    scheme = environ.get('HTTP_X_SCHEME', '')
    if scheme:
        environ['wsgi.url_scheme'] = scheme

    return _application(environ, start_response)
