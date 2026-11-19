FROM scratch
ADD python-files.tar /
COPY app/ /app/
USER 10001:10001
CMD ["python3", "/app/status.py", "--listen", "0.0.0.0"]
