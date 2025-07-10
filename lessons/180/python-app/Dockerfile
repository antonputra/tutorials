FROM python:3.14-rc-alpine3.20

WORKDIR /app

RUN apk update && apk add linux-headers && apk add g++

COPY . .

RUN pip install -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
