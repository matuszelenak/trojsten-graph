#!/bin/sh

if [ "$DATABASE" = "graph" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python manage.py build_enums
PYTHONDONTWRITEBYTECODE=1 DJANGO_SETTINGS_MODULE=graph.settings.collect_static python3 manage.py collectstatic --no-input -i rest_framework -i debug_toolbar

exec "$@"
