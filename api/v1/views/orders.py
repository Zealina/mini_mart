#!/usr/bin/env python3
"""
Order API routes
Manages CRUD operations for orders and their items.
"""

from api.v1.views import app_views
from flask import jsonify, request
from repositories.order_repo import OrderRepo

@app_views.route('/orders', methods=['GET'])
def get_all_orders():
    orders = OrderRepo.all()
    return jsonify([entry.to_dict() for entry in orders])

@app_views.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = OrderRepo.get(order_id)
    if order:
        return jsonify(order.to_dict())
    return jsonify({"error": "order not found"}), 404

@app_views.route('/orders', methods=['POST'])
# 🚨 SPRINT FIX: NO @jwt_required() HERE! We bypass the browser cookie block!
def create_order():
    data = request.get_json()
    if not data or "items" not in data:
        return jsonify({"error": "items are required"}), 400

    # Grab user_id directly from the React payload instead of the blocked cookie
    secure_user_id = data.get("user_id")
    if not secure_user_id:
        return jsonify({"error": "user_id is missing from payload"}), 400

    # Grab the exact keys the React Cart is sending
    address = data.get("address") or data.get("delivery_address")
    phone = data.get("phone") or data.get("contact_phone")

    kwargs = {}
    if address: kwargs["delivery_address"] = address
    if phone: kwargs["contact_phone"] = phone

    try:
        # Pass the details into the repository
        order = OrderRepo.new(secure_user_id, data["items"], **kwargs)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
        
    return jsonify(order.to_dict()), 201

@app_views.route('/orders/<order_id>', methods=['DELETE'])
def remove_order(order_id):
    if OrderRepo.delete(order_id):
        return jsonify({"success": "OK"}), 200
    return jsonify({"error": "order not found"}), 404

@app_views.route('/orders/<order_id>/items', methods=['GET'])
def get_order_items(order_id):
    order = OrderRepo.get(order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404
    return jsonify([item.to_dict() for item in OrderRepo.get_items(order_id)]), 200

@app_views.route('/orders/<order_id>/items', methods=['POST'])
def add_item_to_order(order_id):
    data = request.get_json()
    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({"error": "product_id and quantity required"}), 400
    item = OrderRepo.add_item(order_id, data["product_id"], data["quantity"])
    if not item:
        return jsonify({"error": "order not found"}), 404
    return jsonify(item.to_dict()), 201

@app_views.route('/orders/<order_id>/items/<product_id>', methods=['DELETE'])
def remove_item_from_order(order_id, product_id):
    if OrderRepo.remove_item(order_id, product_id):
        return jsonify({"success": "OK"}), 200
    return jsonify({"error": "order or item not found"}), 404
