#!/usr/bin/env python3
"""User Authentication"""

from api.v1.views import app_views
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from repositories.user_repo import UserRepo
from functools import wraps


@app_views.route("/login", methods=["POST"])
def login():
    """
    User login
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
          required: [email, password]
    responses:
      200:
        description: Successful login
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            user:
              type: object
              properties:
                id:
                  type: string
                  format: uuid
                email:
                  type: string
      400:
        description: Missing email or password
      401:
        description: Incorrect credentials
    """
    email = request.json.get("email")
    password = request.json.get("password")
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = UserRepo.get_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({"error": "Incorrect email or password"}), 401

    access_token = create_access_token(
            identity=user.id,
            additional_claims={"is_admin": user.is_admin})
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    ), 200


@app_views.route("/register", methods=["POST"])
def register():
    """
    User registration
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/User'
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            message:
              type: string
            id:
              type: string
              format: uuid
            email:
              type: string
      400:
        description: Invalid input
    """
    data = request.get_json()
    try:
        new_user = UserRepo.new(**data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(
        {"message": "User registered successfully", "id": new_user.id, "email": new_user.email}
    ), 201


@app_views.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: New access token issued
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Invalid or missing refresh token
    """
    current_user_id = get_jwt_identity()
    user = UserRepo.get(current_user_id)
    n_tk = create_access_token(identity=current_user_id,
                               additional_claims={"is_admin": user.is_admin})
    return jsonify(access_token=n_tk), 200

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("is_admin"):
                return fn(*args, **kwargs)
            else:
                return jsonify(error="admins only!"), 403

        return decorator

    return wrapper
