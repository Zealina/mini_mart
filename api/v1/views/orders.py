#!/usr/bin/env python3
"""
Order API routes
Manages CRUD operations for orders and their items.
"""

from api.v1.views import app_views
from flask import jsonify, request
from repositories.order_repo import OrderRepo
from flask_jwt_extended import jwt_required, get_jwt_identity

@app_views.route('/orders', methods=['GET'])
def get_all_orders():
    """Get all orders"""
    orders = OrderRepo.all()
    orders = [entry.to_dict() for entry in orders]
    return jsonify(orders)

@app_views.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get an order by ID"""
    order = OrderRepo.get(order_id)
    if order:
        return jsonify(order.to_dict())
    return jsonify({"error": "order not found"}), 404

@app_views.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order"""
    data = request.get_json()
    if not data or "items" not in data:
        return jsonify({"error": "items are required"}), 400
    
    secure_user_id = get_jwt_identity()
    
    # ✅ STRICT EXTRACTION - Maps perfectly to Cart.jsx payload
    address = data.get("address", "Not provided")
    phone = data.get("phone", "Not provided")
        
    try:
        # ✅ EXPLICIT PASSING
        order = OrderRepo.new(secure_user_id, data["items"], address=address, phone=phone)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
        
    return jsonify(order.to_dict()), 201

@app_views.route('/orders/<order_id>', methods=['DELETE'])
def remove_order(order_id):
    """Delete an order"""
    deleted = OrderRepo.delete(order_id)
    if deleted:
        return jsonify({"success": "OK"}), 200
    return jsonify({"error": "order not found"}), 404

@app_views.route('/orders/<order_id>/items', methods=['GET'])
def get_order_items(order_id):
    """Get all items in an order"""
    order = OrderRepo.get(order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404
    items = OrderRepo.get_items(order_id)
    return jsonify([item.to_dict() for item in items]), 200

@app_views.route('/orders/<order_id>/items', methods=['POST'])
def add_item_to_order(order_id):
    """Add an item to an order"""
    data = request.get_json()
    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({"error": "product_id and quantity required"}), 400
    item = OrderRepo.add_item(order_id, data["product_id"], data["quantity"])
    if not item:
        return jsonify({"error": "order not found"}), 404
    return jsonify(item.to_dict()), 201

@app_views.route('/orders/<order_id>/items/<product_id>', methods=['DELETE'])
def remove_item_from_order(order_id, product_id):
    """Remove an item from an order"""
    removed = OrderRepo.remove_item(order_id, product_id)
    if not removed:
        return jsonify({"error": "order or item not found"}), 404
    return jsonify({"success": "OK"}), 200
