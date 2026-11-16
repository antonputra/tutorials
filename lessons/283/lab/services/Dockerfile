# One image for Harbor's services and the learner's toolbox: Python 3.14 with the lab's pinned libraries, curl and jq.
FROM python:3.14.10-slim@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f
RUN apt-get update && apt-get install -y --no-install-recommends curl jq && rm -rf /var/lib/apt/lists/*
WORKDIR /harbor
COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt -c constraints.txt
COPY *.py ./
# `harbor` runs the helpers with Python by name, so a Windows checkout with CRLF line endings still works.
RUN printf '#!/bin/sh\nexec python /harbor/harbor.py "$@"\n' > /usr/local/bin/harbor && chmod +x /usr/local/bin/harbor
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/harbor
