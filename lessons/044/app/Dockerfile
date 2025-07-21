FROM python:3.14-rc-alpine3.20

WORKDIR /app

COPY requirements.txt .

RUN addgroup -S flask && \
  adduser -S flask -G flask && \
  pip install -r requirements.txt

COPY src/ .

USER flask

ENTRYPOINT [ "python3", "./server.py" ]
