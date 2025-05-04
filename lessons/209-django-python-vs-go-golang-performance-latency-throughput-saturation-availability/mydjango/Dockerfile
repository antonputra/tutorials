FROM python:3.12.6-slim-bookworm AS build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

FROM python:3.12.6-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY . /app

# A general rule of thumb is to run (2 x $num_cores) + 1 workers, 
# where $num_cores is the number of CPU cores available to the container.
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8080", "mydjango.wsgi:application"]
