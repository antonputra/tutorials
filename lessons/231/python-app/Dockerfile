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
# CMD ["uvicorn", "main:app", "--workers", "2", "--no-access-log"]

# 4 for the second test to achieve full CPU utilization
CMD ["uvicorn", "main:app", "--workers", "4", "--no-access-log"]
