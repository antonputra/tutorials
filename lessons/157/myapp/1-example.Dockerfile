FROM python:3.14-rc-slim

COPY main.py .

ENTRYPOINT [ "python3", "main.py"]
