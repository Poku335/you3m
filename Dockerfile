# Multi-stage build
FROM node:18-alpine AS frontend-build

# Build frontend
WORKDIR /app/frontend
COPY web_youtube_converter/frontend/package.json ./
RUN npm install
COPY web_youtube_converter/frontend/ ./
RUN npm run build

# Python backend
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY web_youtube_converter/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY web_youtube_converter/backend/ ./

# Copy built frontend
COPY --from=frontend-build /app/frontend/build ./static/

# Create directories
RUN mkdir -p media staticfiles

# Skip static files collection for now
# RUN python manage.py collectstatic --noinput --settings=youtube_converter.settings_production || echo "Static files collection failed, continuing..."

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--settings=youtube_converter.settings_production"]