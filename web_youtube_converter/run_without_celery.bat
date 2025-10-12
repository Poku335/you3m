@echo off
echo Starting Django in synchronous mode (no Celery needed)...
cd backend
call venv\Scripts\activate
set DJANGO_SETTINGS_MODULE=youtube_converter.settings_no_redis
python manage.py runserver