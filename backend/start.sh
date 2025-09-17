#!/bin/bash
# Render deployment startup script

echo "Starting Student Performance Dashboard API..."

# Initialize models if they don't exist
echo "Checking and initializing models..."
python scripts/init_models.py

if [ $? -ne 0 ]; then
    echo "Model initialization failed, but continuing with startup..."
fi

# Start the FastAPI application
echo "Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
