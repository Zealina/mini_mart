#!/usr/bin/env python3
"""
Order API routes
Manages CRUD operations for orders and their items.

Document flow:
  1. Customer checks out and uploads proof of their bank transfer
     (an image or PDF) -> stored on disk as `payment_proof`.
  2. An INVOICE is generated immediately, status "Pending Payment
     Confirmation" -> this is what gets emailed to the customer first.
  3. Once the store owner reviews the payment_proof and confirms the
     transfer actually landed, POST /orders/<id>/confirm-payment
     generates the official RECEIPT and marks the order Paid -> this
     is the second document, emailed once payment is confirmed.
"""

import json
import os
import uuid
from datetime import datetime

from api.v1.views import app_views
from api.v1.views.auth import admin_required
from flask import current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from repositories.order_repo import OrderRepo
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
PAYMENT_PROOFS_SUBDIR = "payment_proofs"
INVOICES_SUBDIR = "invoices"
RECEIPTS_SUBDIR = "receipts"

ALLOWED_PROOF_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "heic", "heif", "pdf"}
MAX_PROOF_SIZE_BYTES = 10 * 1024 * 1024  # 10MB, mirrors the frontend limit

PAID_STATUS = "Paid"
PENDING_STATUS = "Pending Payment Confirmation"


def _ensure_upload_dirs():
    """Make sure uploads/payment_proofs, uploads/invoices, uploads/receipts exist."""
    for subdir in (PAYMENT_PROOFS_SUBDIR, INVOICES_SUBDIR, RECEIPTS_SUBDIR):
        os.makedirs(os.path.join(UPLOAD_FOLDER, subdir), exist_ok=True)


def _allowed_proof_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_PROOF_EXTENSIONS


def _save_payment_proof(file_storage, user_id):
    """Persist the customer's uploaded transfer proof to disk and return its URL."""
    original_name = secure_filename(file_storage.filename or "")
    if not original_name or not _allowed_proof_file(original_name):
        raise ValueError("payment proof must be an image (png/jpg/webp/heic) or a pdf")
    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > MAX_PROOF_SIZE_BYTES:
        raise ValueError(f"payment proof exceeds the {MAX_PROOF_SIZE_BYTES // (1024 * 1024)}MB limit")

    ext = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{user_id}_{uuid.uuid4().hex}.{ext}"

    _ensure_upload_dirs()
    disk_path = os.path.join(UPLOAD_FOLDER, PAYMENT_PROOFS_SUBDIR, unique_name)
    file_storage.save(disk_path)

    return f"/uploads/{PAYMENT_PROOFS_SUBDIR}/{unique_name}"


def _order_line_items(order):
    """Shared helper: returns (line_items, total) for the order's items."""
    line_items = []
    total = 0
    for item in OrderRepo.get_items(order.id):
        product = getattr(item, "product", None)
        name = getattr(product, "name", None) or getattr(item, "product_id", "Item")
        price = float(getattr(item, "price", None) or getattr(product, "price", 0) or 0)
        qty = int(getattr(item, "quantity", 0))
        subtotal = price * qty
        total += subtotal
        line_items.append((str(name), qty, price, subtotal))
    return line_items, total


def _render_pdf_document(disk_path, order, heading, footer_note=None):
    """
    Shared PDF layout used for both the invoice and the receipt -- same
    order details and line items, different heading/footer so the two
    documents are visually distinguishable.

    Requires reportlab (`pip install reportlab`).
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(disk_path, pagesize=A4)
    width, height = A4
    y = height - 25 * mm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y, f"CEXPRESS MINIMART - {heading}")

    y -= 10 * mm
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, f"Order ID: {order.id}")
    y -= 6 * mm
    c.drawString(20 * mm, y, f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    y -= 6 * mm
    c.drawString(20 * mm, y, f"Delivery Address: {getattr(order, 'delivery_address', '') or 'N/A'}")
    y -= 6 * mm
    c.drawString(20 * mm, y, f"Contact Phone: {getattr(order, 'contact_phone', '') or 'N/A'}")

    y -= 12 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, "Item")
    c.drawString(120 * mm, y, "Qty")
    c.drawString(145 * mm, y, "Price")
    c.drawString(170 * mm, y, "Subtotal")
    y -= 4 * mm
    c.line(20 * mm, y, 190 * mm, y)

    c.setFont("Helvetica", 10)
    line_items, total = _order_line_items(order)
    for name, qty, price, subtotal in line_items:
        y -= 7 * mm
        if y < 35 * mm:
            c.showPage()
            y = height - 25 * mm
            c.setFont("Helvetica", 10)

        c.drawString(20 * mm, y, name[:45])
        c.drawString(120 * mm, y, str(qty))
        c.drawString(145 * mm, y, f"{price:,.2f}")
        c.drawString(170 * mm, y, f"{subtotal:,.2f}")

    y -= 10 * mm
    c.line(20 * mm, y, 190 * mm, y)
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(140 * mm, y, f"Total: NGN {total:,.2f}")

    if footer_note:
        y -= 12 * mm
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(20 * mm, y, footer_note)

    c.showPage()
    c.save()


def _generate_invoice(order):
    """
    Generate the first document sent to the customer: an invoice showing
    the order is pending payment confirmation. Returns its public URL.
    """
    _ensure_upload_dirs()
    invoice_filename = f"invoice_{order.id}.pdf"
    disk_path = os.path.join(UPLOAD_FOLDER, INVOICES_SUBDIR, invoice_filename)

    _render_pdf_document(
        disk_path,
        order,
        heading="Invoice (Pending Payment Confirmation)",
        footer_note="This invoice will be followed by an official receipt once your payment is confirmed.",
    )

    return f"/uploads/{INVOICES_SUBDIR}/{invoice_filename}"


def _generate_receipt(order):
    """
    Generate the second document, sent only once the owner has confirmed
    the transfer landed. Returns its public URL.
    """
    _ensure_upload_dirs()
    receipt_filename = f"receipt_{order.id}.pdf"
    disk_path = os.path.join(UPLOAD_FOLDER, RECEIPTS_SUBDIR, receipt_filename)

    _render_pdf_document(
        disk_path,
        order,
        heading="Official Receipt",
        footer_note="Payment received and confirmed. Thank you for your order!",
    )

    return f"/uploads/{RECEIPTS_SUBDIR}/{receipt_filename}"


@app_views.route('/uploads/<subdir>/<filename>', methods=['GET'])
@jwt_required()
def get_uploaded_file(subdir, filename):
    """Serve a saved payment proof, invoice, or receipt file from disk."""
    if subdir not in (PAYMENT_PROOFS_SUBDIR, INVOICES_SUBDIR, RECEIPTS_SUBDIR):
        return jsonify({"error": "not found"}), 404
    directory = os.path.join(UPLOAD_FOLDER, subdir)
    return send_from_directory(directory, secure_filename(filename))


@app_views.route('/orders', methods=['GET'])
@jwt_required()
def get_all_orders():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    orders = OrderRepo.all()
    if not claims.get("is_admin"):
        orders = [order for order in orders if order.user_id == current_user_id]
    return jsonify([entry.to_dict() for entry in orders]), 200

@app_views.route('/orders/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    order = OrderRepo.get(order_id)
    if order and not get_jwt().get("is_admin"):
        if order.user_id != get_jwt_identity():
            return jsonify({"error": "order not found"}), 404
    if order:
        return jsonify(order.to_dict())
    return jsonify({"error": "order not found"}), 404

@app_views.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    is_multipart = bool(request.content_type) and "multipart/form-data" in request.content_type

    if is_multipart:
        items_raw = request.form.get("items")
        try:
            items = json.loads(items_raw) if items_raw else None
        except (TypeError, ValueError):
            return jsonify({"error": "items must be valid JSON"}), 400
        address = request.form.get("address") or request.form.get("delivery_address")
        phone = request.form.get("phone") or request.form.get("contact_phone")
        proof_file = request.files.get("receipt") 
    else:
        data = request.get_json() or {}
        items = data.get("items")
        address = data.get("address") or data.get("delivery_address")
        phone = data.get("phone") or data.get("contact_phone")
        proof_file = None

    if not items:
        return jsonify({"error": "items are required"}), 400

    if not proof_file or not proof_file.filename:
        return jsonify({"error": "payment proof (image or pdf) is required"}), 400

    secure_user_id = get_jwt_identity()

    try:
        payment_proof_url = _save_payment_proof(proof_file, secure_user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    kwargs = {"payment_proof_url": payment_proof_url, "status": PENDING_STATUS}
    if address: kwargs["delivery_address"] = address
    if phone: kwargs["contact_phone"] = phone

    try:
        order = OrderRepo.new(secure_user_id, items, **kwargs)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        invoice_url = _generate_invoice(order)
        OrderRepo.update_invoice_url(order.id, invoice_url)
        order.invoice_url = invoice_url
    except Exception as e:
        current_app.logger.error(f"Failed to generate invoice for order {order.id}: {e}")
    print(order.__dict__)
    print("----- To json ------")
    print(json.dumps(order.to_dict()))
    return jsonify(order.to_dict()), 201

@app_views.route('/orders/<order_id>/confirm-payment', methods=['POST'])
@jwt_required()
@admin_required()
def confirm_order_payment(order_id):
    """
    Owner-only: called after reviewing the customer's uploaded payment_proof
    and confirming the transfer actually landed. Marks the order Paid and
    generates the official receipt -- document #2, emailed separately from
    the invoice.
    """
    order = OrderRepo.get(order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404

    OrderRepo.update_status(order_id, PAID_STATUS)

    try:
        receipt_url = _generate_receipt(order)
        OrderRepo.update_receipt_url(order_id, receipt_url)
    except Exception as e:
        current_app.logger.error(f"Failed to generate receipt for order {order_id}: {e}")
        return jsonify({"error": "payment confirmed but receipt generation failed"}), 500

    order = OrderRepo.get(order_id)
    return jsonify(order.to_dict()), 200

@app_views.route('/orders/<order_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def remove_order(order_id):
    if OrderRepo.delete(order_id):
        return jsonify({"success": "OK"}), 200
    return jsonify({"error": "order not found"}), 404

@app_views.route('/orders/<order_id>/items', methods=['GET'])
@jwt_required()
def get_order_items(order_id):
    order = OrderRepo.get(order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404
    return jsonify([item.to_dict() for item in OrderRepo.get_items(order_id)]), 200

@app_views.route('/orders/<order_id>/items', methods=['POST'])
@jwt_required()
@admin_required()
def add_item_to_order(order_id):
    data = request.get_json()
    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({"error": "product_id and quantity required"}), 400
    item = OrderRepo.add_item(order_id, data["product_id"], data["quantity"])
    if not item:
        return jsonify({"error": "order not found"}), 404
    return jsonify(item.to_dict()), 201

@app_views.route('/orders/<order_id>/items/<product_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def remove_item_from_order(order_id, product_id):
    if OrderRepo.remove_item(order_id, product_id):
        return jsonify({"success": "OK"}), 200
    return jsonify({"error": "order or item not found"}), 404
@app_views.route('/orders/<order_id>/status', methods=['PUT'])
@jwt_required()
@admin_required()
def update_order_status(order_id):
    """
    Update order fulfillment status (Processing, Dispatched, Delivered).
    Note: to mark payment as confirmed and trigger the receipt, use
    POST /orders/<order_id>/confirm-payment instead of this endpoint.
    """
    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"error": "status is required"}), 400
    
    updated = OrderRepo.update_status(order_id, data["status"])
    if updated:
        return jsonify({"success": "OK", "status": data["status"]}), 200
        
    return jsonify({"error": "order not found"}), 404
