import random
import time
from flask import Flask
from prometheus_client import Histogram, generate_latest


version = 'v3'
max_latency = 10
error_rate = 0.05

if version == 'v2':
    max_latency = 40
    error_rate = 0.50

buckets = (.1, .25, .5, .75, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.1,
           2.25, 2.5, 2.75, 3.0, 3.0, 3.1, 3.25, 3.5, 3.75, 4.0)

request_duration = Histogram(name='request_duration_seconds',
                             documentation='Time spent processing request',
                             labelnames=['status'],
                             buckets=buckets)

app = Flask(__name__)


@app.route('/metrics')
def metrics():
    return generate_latest()


@app.route('/version', methods=['GET'])
def get_version():
    status = 201

    start = time.time()
    sleep(max_latency)
    end = time.time() - start

    if random.random() < error_rate:
        status = 404

    request_duration.labels(status).observe(end)

    return {'version': version}, status


def sleep(max):
    time.sleep(random.randint(0, max) * 0.1)
