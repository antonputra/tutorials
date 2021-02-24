FROM python:3.9.1-alpine3.12

WORKDIR /app

COPY requirements.txt .

RUN addgroup -S flask && \
  adduser -S flask -G flask && \
  pip install -r requirements.txt

COPY src/ .

USER flask

ENTRYPOINT [ "python3", "./server.py" ]
