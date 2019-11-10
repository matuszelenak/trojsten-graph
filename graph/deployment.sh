#!/bin/bash
python manage.py migrate
python manage.py loaddata initial
python manage.py collectstatic --noinput
python manage.py build_enums

gunicorn --bind 0.0.0.0:$PORT graph.wsgi --env DJANGO_SETTINGS_MODULE=graph.settings.production --log-level DEBUG --access-logfile - --log-file -
