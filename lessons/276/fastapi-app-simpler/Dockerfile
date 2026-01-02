FROM python:3.14.2-trixie AS build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

FROM python:3.14.2-slim-trixie

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=build /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages

COPY --from=build /usr/local/bin/gunicorn /usr/local/bin/gunicorn

COPY ./src /app
COPY ./config.yaml /app/config.yaml

RUN chown -R app:app /app

ENV PYTHONHASHSEED=random
ENV MALLOC_ARENA_MAX=2

USER app

CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--preload", "--timeout", "10", "--graceful-timeout", "5", "--log-level", "error", "main:app", "--bind", "0.0.0.0:8080"]
