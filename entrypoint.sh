#!/bin/sh
set -e

python manage.py migrate
python manage.py loaddata groups
python manage.py ensure_admin

exec "$@"
