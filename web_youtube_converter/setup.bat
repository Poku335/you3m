@echo off
echo Setting up YouTube to MP3 Converter Web App...

echo.
echo Setting up Backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

echo.
echo Setting up Frontend...
cd ..\frontend
npm install

echo.
echo Setup completed!
echo.
echo To run the application:
echo 1. Start Redis server
echo 2. Run: cd backend && venv\Scripts\activate && python manage.py runserver
echo 3. Run: cd backend && venv\Scripts\activate && celery -A youtube_converter worker --loglevel=info
echo 4. Run: cd frontend && npm start
echo.
pause