#!/usr/bin/env python3
"""Manage products"""

import os
import uuid
from flask import (
    jsonify, request, current_app
)
from api.v1.views import app_views
from api.v1.views.auth import admin_required
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from repositories.product_repo import ProductRepo

from dotenv import load_dotenv
load_dotenv()


ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "webp", "svg", "ico"
}
UPLOAD_FOLDER = "/var/www/cexpressminimart-uploads/"
PUBLIC_URL_PREFIX = "/uploads"

@app_views.route('/products', methods=['GET'])
def get_all_products():
    """Get all products"""
    prod_list = ProductRepo.all()
    prod_list = [entry.to_dict() for entry in prod_list]
    return jsonify(prod_list)

@app_views.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    product = ProductRepo.get(product_id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({"error": "product not found"}), 404

@app_views.route('/products', methods=['POST'])
@jwt_required()
@admin_required()
def create_product():
    """Create a new product"""
    if 'image' not in request.files:
        return jsonify({"error": "no image file provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "no file selected"}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({
            "error": "invalid file type",
            "message": f"allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        }), 400

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
    if size > MAX_FILE_SIZE_BYTES:
        return jsonify({"error": "file too large", "message": "max size is 5MB"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    safe_name = secure_filename(unique_name)
    disk_path = os.path.join(UPLOAD_FOLDER, safe_name)

    try:
        file.save(disk_path)
    except Exception as e:
        print(e)
        return jsonify({"error": "failed to save file", "message": str(e)}), 500

    data = request.form.to_dict()
    image_url = f"{PUBLIC_URL_PREFIX}/{safe_name}"
    data["image_url"] = image_url

    try:
        new = ProductRepo.new(**data)
    except ValueError as e:
        if os.path.exists(disk_path):
            os.remove(disk_path)
        return jsonify({"error": "incorrect/incomplete parameters", "message": str(e)}), 400
    return jsonify(new.to_dict()), 201

@app_views.route('/products/<product_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_product(product_id):
    """Update an existing product"""
    product = ProductRepo.get(product_id)
    if not product:
        return jsonify({"error": "product not found"}), 404

    image_url = None
    images = request.files.getlist("images")

    if images:
        image = images[0]
        new_url = save_image(image)
        if not new_url:
            return jsonify({"error": "invalid image type or upload failed"}), 400
        
        if getattr(product, "image_url", None) and 'res.cloudinary.com' in product.image_url:
            try:
                public_id = product.image_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(public_id)
            except Exception as e:
                print(f"Could not remove old image from Cloudinary: {e}")
                
        image_url = new_url

    data = request.form.to_dict() if not request.is_json else request.get_json()
    if image_url:
        data["image_url"] = image_url

    res = ProductRepo.update(product_id, **data)
    return jsonify(res.to_dict()), 200

@app_views.route('/products/category/<category_id>', methods=['GET'])
def get_products_by_category(category_id):
    """Get products by category"""
    products = ProductRepo.get_products_by_category(category_id)
    if not products:
        return jsonify({"error": "category not found"}), 404
    return jsonify([product.to_dict() for product in products]), 200

@app_views.route('/products/<product_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def remove_product(product_id):
    """Delete a product"""
    product = ProductRepo.get(product_id)
    if not product:
        return jsonify({"error": "product not found"}), 404

    # Delete the image from Cloudinary
    if getattr(product, "image_url", None) and 'res.cloudinary.com' in product.image_url:
        try:
            public_id = product.image_url.split('/')[-1].split('.')[0]
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            print(f"Could not remove image from Cloudinary: {e}")

    deleted = ProductRepo.delete(product_id)
    if deleted:
        return jsonify({"success": "OK"}), 200

    return jsonify({"error": "product not found"}), 404
