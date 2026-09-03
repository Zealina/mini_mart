#!/usr/bin/env python3
"""Manage users"""

from api.v1.views import app_views
from api.v1.views.auth import super_admin_required
from flask import jsonify, request
from models import storage
from models.user import User
from models.pending_staff_access import PendingStaffAccess
from repositories.user_repo import UserRepo
from sqlalchemy.exc import IntegrityError

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

    try:
        new = UserRepo.new(**data)
    except IntegrityError:
        storage.rollback()
        return jsonify({"error": "An account with this Email or WhatsApp number already exists."}), 400
    except ValueError as e:
        print(f"Error: {e}")
        return jsonify({
            "error": "incorrect/incomplete parameters",
            "message": str(e)
        }), 400

    pending_access = storage.get_by_attr(
        PendingStaffAccess,
        email=(new.email or '').strip().lower()
    )
    if pending_access:
        updated = UserRepo.update(
            id=new.id,
            is_admin=True,
            is_super_admin=pending_access.role == 'super_admin'
        )
        storage.delete(pending_access)
        storage.save()
        new = updated

    from email_service import send_welcome_email

    send_welcome_email(new)
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


@app_views.route('/users/access', methods=['POST'])
@super_admin_required()
def grant_staff_access():
    """Grant admin or super-admin access to an existing account by email."""
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    role = data.get('role', 'sub_admin')
    if not email or role not in ('sub_admin', 'super_admin'):
        return jsonify({"error": "email and a valid role are required"}), 400

    user = UserRepo.get_by_email(email)
    if not user:
        pending = storage.get_by_attr(PendingStaffAccess, email=email)
        if pending:
            pending.role = role
            pending.save()
        else:
            PendingStaffAccess(email=email, role=role).save()
        return jsonify({"message": f"Staff access saved for {email}. It will activate when they register.", "pending": True}), 202

    updated = UserRepo.update(
        id=user.id,
        is_admin=True,
        is_super_admin=role == 'super_admin'
    )
    return jsonify(updated.to_dict()), 200


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
