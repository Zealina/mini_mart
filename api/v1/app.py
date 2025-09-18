#!/usr/bin/env python3
"""Rest API"""

from flask import Flask, jsonify
from datetime import datetime
from api.v1.views import app_views


app = Flask(__name__)
app.register_blueprint(app_views)


@app.route("/", methods=["GET"])
def index():
    """Return the homepage"""
    resp = {"status": "OK", "time": datetime.utcnow()}
    return jsonify(resp)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
