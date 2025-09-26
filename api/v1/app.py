#!/usr/bin/env python3
"""Rest API"""
from flask import Flask, jsonify
from datetime import datetime
from api.v1.views import app_views
from flasgger import Swagger
from models import storage
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from werkzeug.exceptions import RequestEntityTooLarge
import logging
from logging.handlers import RotatingFileHandler
import os


load_dotenv()


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

if not os.path.exists("logs"):
    os.makedirs("logs")

log_file = os.path.join("logs", "app.log")

handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s [in %(pathname)s:%(lineno)d]"
)
handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


UPLOAD_FOLDER = os.path.join(os.getcwd(), "assets")
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Mini Mart API",
        "description": "API documentation for Mini Mart",
        "version": "1.0.0"
    },
    "definitions": {
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "email": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"},
                "phone_number": {"type": "string"},
                "whatsapp_number": {"type": "string"},
                "address": {"type": "string"},
                "password": {"type": "string"},
                "is_admin": {"type": "bool"}
            },
            "required": ["email", "first_name", "last_name", "password", "whatsapp_number"]
        },
        "Product": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "price": {"type": "number"},
                "stock": {"type": "integer"},
                "category_id": {"type": "string", "format": "uuid"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            },
            "required": ["name", "price", "stock"]
        },
        "Category": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "name": {"type": "string"},
                "parent_id": {"type": "string", "format": "uuid"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
    },
            "required": ["name"]
        },
        "Order": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "user_id": {"type": "string", "format": "uuid"},
                "completed": {"type": "bool"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"},
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/OrderItem"}
                }
            },

        },
        "OrderItem": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "order_id": {"type": "string", "format": "uuid"},
                "product_id": {"type": "string", "format": "uuid"},
                "quantity": {"type": "integer"}
            }
        }
    }
}

swagger = Swagger(app, template=swagger_template)

app.register_blueprint(app_views)

@app.route("/", methods=["GET"])
def index():
    """Root endpoint """
    resp = {"status": "OK", "time": datetime.now()}
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

@app.errorhandler(RequestEntityTooLarge)
def handle_large_request(error):
    """Handle file too large errors (413)"""
    return jsonify({"error": "File too large. Maximum size is 5 MB."}), 413

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Cleanup logic after each request"""
    storage.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
