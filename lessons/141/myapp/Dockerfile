FROM python:3.14-rc-slim-bookworm

WORKDIR /app

COPY app.py requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8282

CMD ["gunicorn"  , "--bind", "0.0.0.0:8282", "app:app"]
