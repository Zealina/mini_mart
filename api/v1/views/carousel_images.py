#!/usr/bin/env python3
"""Manage storefront carousel images"""
import os
import uuid
from flask import jsonify, request, current_app
from werkzeug.utils import secure_filename
from api.v1.views import app_views
from repositories.carousel_image_repo import CarouselImageRepo

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

UPLOAD_FOLDER = os.path.join('api', 'v1', 'static', 'uploads', 'carousel')
PUBLIC_URL_PREFIX = '/static/uploads/carousel'


def _allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app_views.route('/carousel-images', methods=['GET'])
def get_carousel_images():
    """Return all carousel images, in display order"""
    images = CarouselImageRepo.all()
    return jsonify([img.to_dict() for img in images])


@app_views.route('/carousel-images', methods=['POST'])
def create_carousel_image():
    """Upload a new carousel image (multipart/form-data, field name 'image')"""
    if 'image' not in request.files:
        return jsonify({"error": "no image file provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "no file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({
            "error": "invalid file type",
            "message": f"allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        }), 400

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE_BYTES:
        return jsonify({"error": "file too large", "message": "max size is 5MB"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    safe_name = secure_filename(unique_name)
    disk_path = os.path.join(UPLOAD_FOLDER, safe_name)

    try:
        file.save(disk_path)
    except Exception as e:
        return jsonify({"error": "failed to save file", "message": str(e)}), 500

    user_id = request.form.get('user_id')

    try:
        new_image = CarouselImageRepo.new(
            image_url=f"{PUBLIC_URL_PREFIX}/{safe_name}",
            filename=safe_name,
            uploaded_by=user_id
        )
    except ValueError as e:
        if os.path.exists(disk_path):
            os.remove(disk_path)
        return jsonify({"error": "incorrect/incomplete parameters", "message": str(e)}), 400

    return jsonify(new_image.to_dict()), 201


@app_views.route('/carousel-images/<image_id>', methods=['DELETE'])
def delete_carousel_image(image_id):
    """Delete a carousel image record and its file on disk"""
    image = CarouselImageRepo.get(image_id)
    if not image:
        return jsonify({"error": "carousel image not found"}), 404

    disk_path = os.path.join(UPLOAD_FOLDER, image.filename)

    CarouselImageRepo.delete(image_id)

    if os.path.exists(disk_path):
        try:
            os.remove(disk_path)
        except OSError:
            pass 

    return jsonify({"message": "carousel image deleted"}), 200
