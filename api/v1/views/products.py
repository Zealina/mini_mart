#!/usr/bin/env python3
"""Manage products"""

from api.v1.views import app_views
from flask import jsonify, request
from repositories.product_repo import ProductRepo


@app_views.route('/', methods=['GET'])
def get_all_products():
    """Return the a json of all products in db"""
    prod_list = ProductRepo.all()
    prod_list = [entry.to_dict() for entry in prod_list]
    return jsonify(prod_list)


@app_views.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Return a product based on id"""
    product = ProductRepo.get(product_id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({"error": "product not found"}), 404


@app_views.route('/create', methods=['POST', 'PUT'])
def create_product():
    """Create a new product"""
    data = request.get_json()
    try:
        new = ProductRepo.new(**data)
    except ValueError as e:
        return jsonify({"error": "incorrect/incomplete parameters", "message": str(e)}), 400
    return jsonify({"success": "product created"}), 201


@app_views.route('/remove/<product_id>', methods=['DELETE'])
def remove_product(product_id):
    """Delete a product"""
    data = ProductRepo.delete(product_id)
    if data:
        return jsonify({"success": "OK"}), 201
    return jsonify({"error": "product not found"})


@app_views.route('/update', methods['PUT'])
def update_product():
    """Update product"""
    data = request.get_json()
    res = ProductRepo.update(**data)
    if not res:
        return jsonify({"error": "product not found"})
    return jsonify({"success": "OK"} )
