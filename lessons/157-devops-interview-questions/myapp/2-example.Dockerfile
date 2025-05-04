FROM python:3.11.2-slim-buster

COPY main.py .

ENTRYPOINT [ "python3", "main.py"]
