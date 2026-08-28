#!/usr/bin/env python3
"""User Authentication"""

from api.v1.views import app_views
from flask import jsonify, request, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    set_refresh_cookies,
    unset_jwt_cookies,
    decode_token
)
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from repositories.user_repo import UserRepo
from functools import wraps
from datetime import datetime, timedelta
from email_service import send_reset_password_email
from sqlalchemy.exc import IntegrityError



@app_views.route("/login", methods=["POST"])
def login():
    """
    User login
    """
    email = request.json.get("email")
    password = request.json.get("password")
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = UserRepo.get_by_email(email)
    if user is None:
        return jsonify({"error": "Account not found. Please check your email."}), 404
    if not user.check_password(password):
        return jsonify({"error": "Incorrect password. Please try again."}), 401

    access_token = create_access_token(
            identity=user.id,
            additional_claims={"is_admin": user.is_admin})
    refresh_token = create_refresh_token(identity=user.id)

    response = make_response(jsonify(
        access_token=access_token,
        user=user.to_dict()
    ))

    set_refresh_cookies(response, refresh_token)
    
    return response, 200


@app_views.route("/register", methods=["POST"])
def register():
    """
    User registration
    """
    data = request.get_json()
    try:
        new_user = UserRepo.new(**data)
    except IntegrityError:
        return jsonify({"error": "An account with this Email or WhatsApp number already exists."}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(
        {"message": "User registered successfully", "id": new_user.id, "email": new_user.email}
    ), 201


@app_views.route("/refresh", methods=["POST"])
@jwt_required(refresh=True, locations=['cookies'])
def refresh():
    """
    Refresh access token
    """
    current_user_id = get_jwt_identity()
    user = UserRepo.get(current_user_id)
    n_tk = create_access_token(identity=current_user_id,
                               additional_claims={"is_admin": user.is_admin})
    return jsonify(access_token=n_tk), 200

@app_views.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    """
    Get logged-in user's profile
    """
    current_user_id = get_jwt_identity()
    user = UserRepo.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200


@app_views.route("/logout", methods=["POST"])
@jwt_required(refresh=True, locations=["cookies"])
def logout():
    response = jsonify({
        "message": "Successfully logged out!",
        })
    unset_jwt_cookies(response)
    return response


@app_views.route("/forgot-password", methods=['POST'])
def send_reset_token():
    data = request.get_json()
    if not data or not data.get("email"):
        return jsonify({"error": "bad_request", "message": "Reset email is required"}), 400
    user = UserRepo.get_by_email(data.get("email"))
    if user:
        reset_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(minutes=15),
                additional_claims={"type": "password_reset"})
        send_reset_password_email(user, reset_token)
    return jsonify ({"status": "OK", "message": "The reset link has been sent"}), 200

@app_views.route("/reset-password", methods=["POST"])
def reset_forgotten_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        return jsonify({"error": "bad_request", "message": "Token and password are required"}), 400
    try:
        decoded = decode_token(token)
        if decoded.get("type") != "password_reset":
            return jsonify({"message: Invalid reset token"}), 401
        user_id = decoded["sub"]
    except Exception as e:
        return jsonify({"message": "Invalid or expired reset token"}), 401
    user = UserRepo.get(user_id)
    if not user:
        return jsonify({"message": "Invalid reset token"}), 401
    user = UserRepo.update(user_id=user_id, password=new_password)

    return jsonify({"message": "Password successfully reset!"}), 200

@app_views.route("/me", methods=["GET"])
@jwt_required()
def user_after_refresh():
    user_id = get_jwt_identity()
    user = UserRepo.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"status": "Success",  "user": user.to_dict()}), 200

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
