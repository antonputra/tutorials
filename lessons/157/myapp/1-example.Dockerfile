FROM python:3.11.2

COPY main.py .

ENTRYPOINT [ "python3", "main.py"]
