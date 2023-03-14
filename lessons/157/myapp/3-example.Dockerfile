FROM gcr.io/distroless/python3-debian11

COPY main.py .

ENTRYPOINT ["python3", "-u", "main.py"]
