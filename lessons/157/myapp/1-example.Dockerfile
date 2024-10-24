FROM python:3.13.0rc2

COPY main.py .

ENTRYPOINT [ "python3", "main.py"]
