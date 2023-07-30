#!/bin/sh

echo 'Waiting for postgres...'

# TODO
# while ! nc -z $DB_HOSTNAME $DB_PORT; do
#     sleep 0.1
# done

echo 'PostgreSQL started'

echo 'Running migrations...'
python manage.py migrate

echo 'Collecting static files...'
python manage.py collectstatic --no-input

echo 'Creating superuser...'
python manage.py createsuperuser --no-input

gunicorn now_u_api.wsgi -b 0.0.0.0:5000

exec "$@"
