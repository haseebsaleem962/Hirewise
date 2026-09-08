# HireWise backend — production image
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (see .dockerignore for exclusions)
COPY . .

# Generate the training dataset, train the ML model and download
# NLTK data — everything gets baked into the image at build time.
RUN python train_model.py

EXPOSE 5000

# Production WSGI server (dev server with debug=True is local-only)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:create_app()"]
