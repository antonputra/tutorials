import socket
from flask import Flask

app = Flask(__name__)


@app.route('/api/info', methods=['GET'])
def get_info():
    info = dict()

    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    info['ip'] = ip
    info['hostname'] = hostname

    return info, 201
