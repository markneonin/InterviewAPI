#! /bin/bash

cd testTask

python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input

exec gunicorn testTask.wsgi --bind 0.0.0.0:8000 --reload