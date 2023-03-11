import random
import time
from flask import Flask, request


app = Flask(__name__)

devices = [{
    "id": 1,
    "mac": "14-BA-17-74-24-1D",
    "firmware": "2.0.6"
}, {
    "id": 1,
    "mac": "14-BA-17-74-24-1D",
    "firmware": "2.0.6"
}]


@app.route("/api/devices", methods=['GET', 'POST'])
def hello_world():
    sleep()
    if request.method == 'POST':
        return {'message': 'Device created!'}, 201
    else:
        return devices, 200


def sleep():
    time.sleep(random.randint(0, 5) * 0.1)
