FROM python:3.12.0a3-alpine3.17

WORKDIR /app

COPY app.py requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8282

CMD ["gunicorn"  , "--bind", "0.0.0.0:8282", "app:app"]
