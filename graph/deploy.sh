#!/bin/bash

PYTHONDONTWRITEBYTECODE=1 DJANGO_SETTINGS_MODULE=graph.settings.collect_static python3 manage.py collectstatic --no-input -i rest_framework -i debug_toolbar
gsutil -m rsync -d -r static gs://trojsten-graph-static/static
gcloud app deploy
