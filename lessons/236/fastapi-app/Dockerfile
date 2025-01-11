FROM python:3.13.1-slim-bookworm AS build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

FROM python:3.13.1-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=build /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

RUN apt update && apt install libuv1 zlib1g -y

COPY . /app

# CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "60", "--graceful-timeout", "60",  "--log-level", "error", "main:app",  "--bind", "0.0.0.0:8080"]
CMD ["python3", "-m", "socketify", "main:app", "-w", "2", "--host", "0.0.0.0", "--port", "8080"]