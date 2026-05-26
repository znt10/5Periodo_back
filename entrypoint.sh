#!/bin/sh
set -e

python manage.py migrate
python manage.py loaddata groups || true
python manage.py ensure_admin || true
python manage.py collectstatic --noinput

exec "$@"
