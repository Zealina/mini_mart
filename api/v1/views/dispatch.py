#!/usr/bin/env python3
"""Dispatch API routes for the dispatch mobile app."""

import base64
import os
import uuid

from flask import current_app, jsonify, request

from api.v1.views import app_views
from models import storage
from models.order import Order


UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
SIGNATURES_SUBDIR = "signatures"


def _ensure_signature_dir():
    os.makedirs(os.path.join(UPLOAD_FOLDER, SIGNATURES_SUBDIR), exist_ok=True)


@app_views.route('/dispatch/orders', methods=['GET'])
def get_dispatch_orders():
    """Fetch orders for dispatch, filtered by rider when requested."""
    rider_id = request.args.get('rider_id')
    all_orders = storage.all(Order)

    if rider_id:
        filtered = [
            order for order in all_orders
            if order.rider_id == rider_id and order.status == 'Assigned'
        ]
    else:
        filtered = [
            order for order in all_orders
            if order.status in ['Paid', 'Pending Payment Confirmation', 'Assigned']
        ]

    return jsonify([order.to_dict() for order in filtered]), 200


@app_views.route('/dispatch/orders/<order_id>/assign', methods=['PUT'])
def assign_rider(order_id):
    """Assign an order to a specific rider."""
    data = request.get_json()
    if not data or "rider_id" not in data:
        return jsonify({"error": "rider_id is required"}), 400

    order = storage.get(Order, order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404

    order.rider_id = data["rider_id"]
    order.status = "Assigned"
    order.save()
    storage.save()

    return jsonify(order.to_dict()), 200


@app_views.route('/dispatch/orders/<order_id>/complete', methods=['POST'])
def complete_delivery(order_id):
    """Save a delivery signature and mark the order as delivered."""
    data = request.get_json()
    if not data or "signature" not in data:
        return jsonify({"error": "signature base64 string is required"}), 400

    order = storage.get(Order, order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404

    try:
        encoded_data = data["signature"].split(',', 1)[-1]
        image_data = base64.b64decode(encoded_data)

        filename = f"sig_{order_id}_{uuid.uuid4().hex[:8]}.png"
        _ensure_signature_dir()
        filepath = os.path.join(UPLOAD_FOLDER, SIGNATURES_SUBDIR, filename)
        with open(filepath, "wb") as signature_file:
            signature_file.write(image_data)

        order.signature_url = f"/uploads/{SIGNATURES_SUBDIR}/{filename}"
        order.status = "Delivered"
        order.save()
        storage.save()

        return jsonify({"success": True, "order": order.to_dict()}), 200
    except Exception as error:
        current_app.logger.error(f"Signature save failed: {error}")
        return jsonify({"error": "Failed to process signature image"}), 500