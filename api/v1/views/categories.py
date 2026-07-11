#!/usr/bin/env python3
"""
Category API routes
This module manages CRUD operations for categories.
"""

from api.v1.views import app_views
from flask import jsonify, request
from repositories.category_repo import CategoryRepo
from api.v1.views.auth import admin_required # ✅ SECURITY IMPORT ADDED

@app_views.route('/categories', methods=['GET'])
def get_all_categories():
    """
    Get all categories
    ---
    tags:
      - Categories
    responses:
      200:
        description: List of categories
        schema:
          type: array
          items:
            $ref: '#/definitions/Category'
    """
    cat_list = CategoryRepo.all()
    cat_list = [entry.to_dict() for entry in cat_list]
    return jsonify(cat_list)

@app_views.route('/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get category by ID
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: string
        required: true
        description: The category UUID
    responses:
      200:
        description: Category object
        schema:
          $ref: '#/definitions/Category'
      404:
        description: Category not found
    """
    category = CategoryRepo.get(category_id)
    if category:
        return jsonify(category.to_dict())
    return jsonify({"error": "category not found"}), 404

@app_views.route('/categories', methods=['POST'])
@admin_required() # ✅ SECURITY RESTORED
def create_category():
    """
    Create a new category
    ---
    tags:
      - Categories
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/Category'
    responses:
      201:
        description: Category created successfully
        schema:
          type: object
          properties:
            success:
              type: string
      400:
        description: Invalid request
    """
    data = request.get_json()
    try:
        new = CategoryRepo.new(**data)
    except ValueError as e:
        return jsonify({
            "error": "incorrect/incomplete parameters",
            "message": str(e)
        }), 400
    return jsonify({"success": "OK"}), 201

@app_views.route('/categories/<category_id>', methods=['PUT'])
@admin_required() # ✅ SECURITY RESTORED
def update_category(category_id):
    """
    Update an existing category
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: string
        required: true
        description: The category UUID
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/Category'
    responses:
      200:
        description: Category updated successfully
        schema:
          type: object
          properties:
            success:
              type: string
      404:
        description: Category not found
    """
    data = request.get_json()
    res = CategoryRepo.update(id=category_id, **data)
    if not res:
        return jsonify({"error": "category not found"}), 404
    return jsonify({"success": "OK"}), 200

@app_views.route('/categories/<category_id>', methods=['DELETE'])
@admin_required() # ✅ SECURITY RESTORED
def remove_category(category_id):
    """
    Delete a category
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: string
        required: true
        description: The category UUID
    responses:
      200:
        description: Category deleted successfully
        schema:
          type: object
          properties:
            success:
              type: string
      404:
        description: Category not found
    """
    data = CategoryRepo.delete(category_id)
    if data:
        return jsonify({"success": "OK"}), 200
    return jsonify({"error": "category not found"}), 404
