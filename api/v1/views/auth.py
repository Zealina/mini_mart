#!/usr/bin/env python3
"""User Authentication"""

from api.v1.views import app_views
from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
from repositories.user_repo import UserRepo


@app_views.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = UserRepo.get_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({"error": "Incorrect email or password"}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token,
        user={"id": user.id, "email": user.email}
    ), 200


@app_views.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    try:
        new_user = UserRepo.new(**data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(
        {"message": "User registered successfully", "id": new_user.id, "email": new_user.email}
    ), 201
