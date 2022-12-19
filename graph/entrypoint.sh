#!/bin/bash

DJANGO_SETTINGS_MODULE=graph.settings.collect_static python manage.py collectstatic --noinput
python manage.py migrate

exec "$@"