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

COPY . /app

# Match the number of CPU cores, which is 2 on m7a.large, for the 1st test to reduce throttling.
# CMD ["fastapi", "run", "--workers", "2", "main.py"]

# 4 for the second test to achieve full CPU utilization
CMD ["gunicorn", 
     "-w", "4", 
     "-k", "uvicorn.workers.UvicornWorker", 
     "--timeout", "60", 
     "--graceful-timeout", "60", 
     "--log-level", "error", 
     "main:app", 
     "--bind", "0.0.0.0:8000"]