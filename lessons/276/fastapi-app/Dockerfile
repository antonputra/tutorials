FROM python:3.14.2-trixie AS build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

FROM python:3.14.2-slim-trixie

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=build /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY ./src /app

CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "10", "--graceful-timeout", "10",  "--log-level", "error", "main:app",  "--bind", "0.0.0.0:8080"]
