#!/usr/bin/env python3
"""Manage products"""

from api.v1.views import app_views
from models.engine import storage
from models.product import Product
from flask import jsonify


@app_views.route('/products', methods=['GET'])
def get_all_products():
    """Return the a json of all products in db"""
    prod_list = storage.all(Product)
    prod_list = [entry.to_dict() for entry in prod_list]
    print(prod_list)
    return jsonify(prod_list)
