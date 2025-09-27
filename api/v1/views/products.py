#!/usr/bin/env python3
"""Manage products"""

import os
import uuid
from flask import (
    jsonify, request, url_for, current_app, send_from_directory
)
from werkzeug.utils import secure_filename
from api.v1.views import app_views
from repositories.product_repo import ProductRepo
from api.v1.views.auth import admin_required


allowed_extensions = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
    ".webp", ".heic", ".heif", ".svg", ".ico", ".jfif", ".avif"
}


def save_image(image):
    """Save an uploaded image with a unique filename, return its URL"""
    ext = os.path.splitext(image.filename)[-1].lower()
    if ext not in allowed_extensions:
        return None

    unique_name = f"{uuid.uuid4().hex}{ext}"
    filename = secure_filename(unique_name)

    saved_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    image.save(saved_path)

    return url_for("app_views.get_image", filename=filename, _external=True)


@app_views.route('/products', methods=['GET'])
@admin_required()
def get_all_products():
    """
    Get all products
    ---
    tags:
      - Products
    responses:
      200:
        description: List of all products
        schema:
          type: array
          items:
            $ref: "#/definitions/Product"
    """
    prod_list = ProductRepo.all()
    prod_list = [entry.to_dict() for entry in prod_list]
    return jsonify(prod_list)


@app_views.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get product by ID
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: string
        required: true
        description: The product UUID
    responses:
      200:
        description: Product found
        schema:
          $ref: "#/definitions/Product"
      404:
        description: Product not found
    """
    product = ProductRepo.get(product_id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({"error": "product not found"}), 404


@app_views.route("/images/<filename>")
def get_image(filename):
    """
    Get product image
    ---
    tags:
      - Products
    parameters:
      - name: filename
        in: path
        type: string
        required: true
        description: Image filename
    responses:
      200:
        description: The image file
        schema:
          type: file
    """
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@app_views.route('/products', methods=['POST'])
def create_product():
    """
    Create a new product
    ---
    tags:
      - Products
    consumes:
      - multipart/form-data
    parameters:
      - name: name
        in: formData
        type: string
        required: true
        description: Product name
      - name: price
        in: formData
        type: number
        required: true
        description: Product price
      - name: description
        in: formData
        type: string
        description: Product description
      - name: stock
        in: formData
        type: number
        description: Product stock available
      - name: category_id
        in: formData
        type: string
        description: Product Category ID
      - name: images
        in: formData
        type: file
        description: Product image file
    responses:
      201:
        description: Product created successfully
        schema:
          $ref: "#/definitions/Product"
      400:
        description: Invalid input or image type
    """
    image_url = None
    images = request.files.getlist("images")

    if images:
        image = images[0]
        image_url = save_image(image)
        if not image_url:
            return jsonify({"error": "invalid image type"}), 400

    data = request.form.to_dict()
    if image_url:
        data["image_url"] = image_url

    try:
        new = ProductRepo.new(**data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(new.to_dict()), 201


@app_views.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """
    Update an existing product
    ---
    tags:
      - Products
    consumes:
      - multipart/form-data
      - application/json
    parameters:
      - name: product_id
        in: path
        type: string
        required: true
        description: The product UUID
      - name: name
        in: formData
        type: string
        description: Product name
      - name: price
        in: formData
        type: number
        description: Product price
      - name: description
        in: formData
        type: string
        description: Product description
      - name: stock
        in: formData
        type: number
        description: Product stock available
      - name: category_id
        in: formData
        type: string
        description: Product Category ID
      - name: images
        in: formData
        type: file
        description: New image file

    responses:
      200:
        description: Product updated successfully
        schema:
          $ref: "#/definitions/Product"
      400:
        description: Invalid input or image type
      404:
        description: Product not found
    """
    product = ProductRepo.get(product_id)
    if not product:
        return jsonify({"error": "product not found"}), 404

    image_url = None
    images = request.files.getlist("images")

    if images:
        image = images[0]
        new_url = save_image(image)
        if not new_url:
            return jsonify({"error": "invalid image type"}), 400
        if getattr(product, "image_url", None):
            try:
                old_filename = os.path.basename(product.image_url)
                old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], old_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            except Exception as e:
                current_app.logger.warning(f"Could not remove old image: {e}")
        image_url = new_url

    data = request.form.to_dict() if not request.is_json else request.get_json()
    if image_url:
        data["image_url"] = image_url

    res = ProductRepo.update(product_id, **data)
    return jsonify(res.to_dict()), 200

@app_views.route('/products/category/<category_id>', methods=['GET'])
def get_products_by_category(category_id):
    """
    Get products by category
    ---
    tags:
      - Products
    parameters:
      - name: category_id
        in: path
        type: string
        required: true
        description: The category UUID
    responses:
      200:
        description: Category products retrieved successfully
      404:
        description: Category not found
    """
    products = ProductRepo.get_products_by_category(category_id)
    if not products:
        return jsonify({"error": "category not found"}), 404
    return jsonify([product.to_dict() for product in products]), 200

@app_views.route('/products/<product_id>', methods=['DELETE'])
def remove_product(product_id):
    """
    Delete a product
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: string
        required: true
        description: The product UUID
    responses:
      200:
        description: Product deleted successfully
      404:
        description: Product not found
    """
    product = ProductRepo.get(product_id)
    if not product:
        return jsonify({"error": "product not found"}), 404

    if getattr(product, "image_url", None):
        try:
            filename = os.path.basename(product.image_url)
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            current_app.logger.warning(f"Could not remove image: {e}")

    deleted = ProductRepo.delete(product_id)
    if deleted:
        return jsonify({"success": "OK"}), 200

    return jsonify({"error": "product not found"}), 404
