from flask import Flask

app = Flask(__name__)


@app.route('/healthz', methods=['GET'])
def about():
    message = "healthy"

    return {'message': message}, 200
