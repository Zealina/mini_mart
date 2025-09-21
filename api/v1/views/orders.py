#!/usr/bin/env python3
"""Manage orders"""

from api.v1.views import app_views
from flask import jsonify, request
from repositories.order_repo import OrderRepo
from flask_jwt_extended import jwt_required, get_jwt_identity


@app_views.route('/orders', methods=['GET'])
@jwt_required()
def get_all_orders():
    """Return JSON of all orders in db"""
    orders = OrderRepo.all()
    orders = [entry.to_dict() for entry in orders]
    return jsonify(orders)


@app_views.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Return an order based on ID"""
    order = OrderRepo.get(order_id)
    if order:
        return jsonify(order.to_dict())
    return jsonify({"error": "order not found"}), 404


@app_views.route('/orders/create', methods=['POST'])
def create_order():
    """
    Create a new order with items.
    Request JSON:
        {
            "user_id": "string",
            "items": {
                "product_id1": quantity,
                "product_id2": quantity
            }
        }
    """
    data = request.get_json()
    if not data or "user_id" not in data or "items" not in data:
        return jsonify({"error": "user_id and items are required"}), 400
    try:
        order = OrderRepo.new(data["user_id"], data["items"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(order.to_dict()), 201


@app_views.route('/orders/<order_id>', methods=['DELETE'])
def remove_order(order_id):
    """Delete an order by ID"""
    deleted = OrderRepo.delete(order_id)
    if deleted:
        return jsonify({"success": "OK"}), 201
    return jsonify({"error": "order not found"}), 404


@app_views.route('/orders/<order_id>/items', methods=['GET'])
def get_order_items(order_id):
    """Return all items in a given order"""
    order = OrderRepo.get(order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404
    items = OrderRepo.get_items(order_id)
    return jsonify([item.to_dict() for item in items]), 200


@app_views.route('/orders/<order_id>/items', methods=['POST'])
def add_item_to_order(order_id):
    """
    Add an item to an order.
    Request JSON:
        {
            "product_id": "string",
            "quantity": int
        }
    """
    data = request.get_json()
    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({"error": "product_id and quantity required"}), 400
    item = OrderRepo.add_item(order_id, data["product_id"], data["quantity"])
    if not item:
        return jsonify({"error": "order not found"}), 404
    return jsonify(item.to_dict()), 201


@app_views.route('/orders/<order_id>/items', methods=['DELETE'])
def remove_item_from_order(order_id):
    """
    Remove an item from an order.
    Request JSON:
        {
            "product_id": "string"
        }
    """
    data = request.get_json()
    if not data or "product_id" not in data:
        return jsonify({"error": "product_id required"}), 400
    removed = OrderRepo.remove_item(order_id, data["product_id"])
    if not removed:
        return jsonify({"error": "order or item not found"}), 404
    return jsonify({"success": "OK"}), 200
