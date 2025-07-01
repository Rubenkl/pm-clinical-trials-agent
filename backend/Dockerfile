# Railway-optimized Dockerfile
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}