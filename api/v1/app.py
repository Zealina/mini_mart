#!/usr/bin/env python3
"""Rest API"""

from flask import Flask, jsonify
from datetime import datetime
from api.v1.views import app_views
from flasgger import Swagger
from models import storage
from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os


load_dotenv()


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

jwt = JWTManager(app)

swagger = Swagger(app)

app.register_blueprint(app_views)


@app.route("/", methods=["GET"])
def index():
    """Root endpoint """
    resp = {"status": "OK", "time": datetime.utcnow()}
    return jsonify(resp)


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Cleanup logic after each request"""
    storage.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
