#!/usr/bin/env python3
"""Manage users"""

from api.v1.views import app_views
from flask import jsonify, request
from models import storage
from models.user import User
from repositories.user_repo import UserRepo

@app_views.route('/users', methods=['GET'])
def get_all_users():
    user_list = UserRepo.all()
    user_list = [entry.to_safe_dict() for entry in user_list]
    return jsonify(user_list)

@app_views.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = UserRepo.get(user_id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({"error": "user not found"}), 404

@app_views.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    data.pop("is_admin", None)
    data.pop("is_super_admin", None)

    import json
    print(f"POST /users accessed this endpoint with {json.dumps(data, indent=2)}")
    try:
        new = UserRepo.new(**data)
    except ValueError as e:
        print(f"Error: {e}")
        return jsonify({
            "error": "incorrect/incomplete parameters",
            "message": str(e)
        }), 400
    return jsonify(new.to_dict()), 201

@app_views.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    
    # ✅ BUG FIX: Pass the ID explicitly as a named argument to the repository
    res = UserRepo.update(id=user_id, **data)
    
    if not res:
        return jsonify({"error": "user not found"}), 404
    return jsonify(res.to_dict()), 200

@app_views.route('/users/<user_id>', methods=['DELETE'])
def remove_user(user_id):
    deleted = UserRepo.delete(user_id)
    if deleted:
        return jsonify({"success": "OK"}), 200
    return jsonify({"error": "user not found"}), 404


@app_views.route('/store-settings', methods=['GET'])
def get_store_settings():
    """Public endpoint for the cart to fetch the current store bank details."""
    all_users = UserRepo.all()

    target_admin = None

    for u in all_users:
        if getattr(u, 'is_super_admin', False) in [True, 1, '1', 'true', 'True']:
            if getattr(u, 'account_number', None):
                target_admin = u
                break

    if not target_admin:
        for u in all_users:
            if getattr(u, 'is_admin', False) in [True, 1, '1', 'true', 'True']:
                if getattr(u, 'account_number', None):
                    target_admin = u
                    break

    if target_admin:
        return jsonify({
            "bank_name": getattr(target_admin, "bank_name", "") or "",
            "account_number": getattr(target_admin, "account_number", "") or "",
            "account_name": getattr(target_admin, "account_name", "") or ""
        }), 200

    return jsonify({"error": "Store settings not found"}), 404
