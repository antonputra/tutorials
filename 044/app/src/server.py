import os
from flask import Flask

server = Flask(__name__)
port = 8080


@server.route("/")
def hello():
    return "Hello DevOps!"


if __name__ == "__main__":
    token = os.environ['TOKEN']
    print(f'Server started on port: {port}, token: {token}')
    server.run(host='0.0.0.0', port=port)
