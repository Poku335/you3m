#!/bin/bash

echo "Building frontend..."
cd frontend
npm ci
npm run build
cd ..

echo "Setting up Django..."
cd backend
pip install -r requirements.txt
python manage.py collectstatic --noinput --settings=youtube_converter.settings_production
python manage.py migrate --settings=youtube_converter.settings_production

echo "Build completed!"