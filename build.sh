#!/usr/bin/env bash
set -e
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py collectstatic --noinput
echo "from django.contrib.auth import get_user_model; U=get_user_model(); U.objects.filter(username='admin').exists() or U.objects.create_superuser('admin','','admin123')" | python manage.py shell

