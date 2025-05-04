FROM python:3.12.4-alpine3.20

RUN apk --no-cache add curl

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
