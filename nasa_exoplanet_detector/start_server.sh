#!/bin/bash

# NASA Exoplanet AI Detector - Auto-clear startup script
echo "🚀 Starting NASA Exoplanet AI Detector..."

# Run migrations first (in case tables don't exist)
echo "📊 Ensuring database tables exist..."
python manage.py makemigrations core
python manage.py migrate

echo "🧹 Clearing previous results..."
# Clear all previous prediction results
python manage.py clear_results

echo "✅ Results cleared!"
echo "🔄 Starting Django development server..."

# Start the Django server
python manage.py runserver
