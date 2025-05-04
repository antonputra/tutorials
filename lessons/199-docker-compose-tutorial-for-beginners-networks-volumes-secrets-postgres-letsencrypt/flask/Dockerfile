FROM python:3.12.4-alpine3.20

# We need curl for the health check
RUN apk --no-cache add curl

WORKDIR /app

# First, copy dependencies only
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copying the app source separately significantly improves 
# build time by using the cache if no new dependencies are added
COPY app.py .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
