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
    """
    Get all orders
    ---
    tags:
      - Orders
    responses:
      200:
        description: List of orders
        schema:
          type: array
          items:
            $ref: '#/definitions/Order'
    """
    orders = OrderRepo.all()
    orders = [entry.to_dict() for entry in orders]
    return jsonify(orders)


@app_views.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """
    Get an order by ID
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: string
        required: true
        description: Order UUID
    responses:
      200:
        description: Order object
        schema:
          $ref: '#/definitions/Order'
      404:
        description: Order not found
    """
    order = OrderRepo.get(order_id)
    if order:
        return jsonify(order.to_dict())
    return jsonify({"error": "order not found"}), 404


@app_views.route('/orders', methods=['POST'])
def create_order():
    """
    Create a new order
    ---
    tags:
      - Orders
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: string
            items:
              type: object
              additionalProperties:
                type: integer
          required: [user_id, items]
    responses:
      201:
        description: Order created successfully
        schema:
          $ref: '#/definitions/Order'
      400:
        description: Invalid request
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
    """
    Delete an order
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Order deleted successfully
      404:
        description: Order not found
    """
    deleted = OrderRepo.delete(order_id)
    if deleted:
        return jsonify({"success": "OK"}), 200
    return jsonify({"error": "order not found"}), 404


@app_views.route('/orders/<order_id>/items', methods=['GET'])
def get_order_items(order_id):
    """
    Get all items in an order
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: List of order items
        schema:
          type: array
          items:
            $ref: '#/definitions/OrderItem'
      404:
        description: Order not found
    """
    order = OrderRepo.get(order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404
    items = OrderRepo.get_items(order_id)
    return jsonify([item.to_dict() for item in items]), 200


@app_views.route('/orders/<order_id>/items', methods=['POST'])
def add_item_to_order(order_id):
    """
    Add an item to an order
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            product_id:
              type: string
            quantity:
              type: integer
          required: [product_id, quantity]
    responses:
      201:
        description: Item added successfully
        schema:
          $ref: '#/definitions/OrderItem'
      404:
        description: Order not found
    """
    data = request.get_json()
    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({"error": "product_id and quantity required"}), 400
    item = OrderRepo.add_item(order_id, data["product_id"], data["quantity"])
    if not item:
        return jsonify({"error": "order not found"}), 404
    return jsonify(item.to_dict()), 201


@app_views.route('/orders/<order_id>/items/<product_id>', methods=['DELETE'])
def remove_item_from_order(order_id, product_id):
    """
    Remove an item from an order
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: string
        required: true
      - name: product_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Item removed successfully
      404:
        description: Order or item not found
    """
    removed = OrderRepo.remove_item(order_id, product_id)
    if not removed:
        return jsonify({"error": "order or item not found"}), 404
    return jsonify({"success": "OK"}), 200
