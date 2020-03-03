web: gunicorn -c gunicorn.conf.py graph.wsgi --env DJANGO_SETTINGS_MODULE=graph.settings.production_heroku --log-level INFO --access-logfile - --log-file -
release: ./heroku-release.sh