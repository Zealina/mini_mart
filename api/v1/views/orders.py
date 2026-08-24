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
from repositories.user_repo import UserRepo
from werkzeug.utils import secure_filename
from email_service import send_order_confirmation_email, send_owner_order_email, send_receipt_email

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
PAYMENT_PROOFS_SUBDIR = "payment_proofs"
INVOICES_SUBDIR = "invoices"
RECEIPTS_SUBDIR = "receipts"

ALLOWED_PROOF_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "heic", "heif", "pdf"}
MAX_PROOF_SIZE_BYTES = 10 * 1024 * 1024  # 10MB, mirrors the frontend limit

PAID_STATUS = "Paid"
PENDING_STATUS = "Pending Payment Confirmation"

# ---------------------------------------------------------------------------
# Branding: logo assets + palette shared by the invoice and receipt PDFs.
# Drop the two PNGs below into BRANDING_DIR (or point BRANDING_DIR at wherever
# they live) -- they ship alongside this file.
#   logo-header.png           wide/horizontal logo lockup, used in the header
#   logo-watermark-faint.png  circular badge logo, alpha pre-baked ~16% for
#                              use as a page watermark
# ---------------------------------------------------------------------------
BRANDING_DIR = os.environ.get("BRANDING_DIR", os.path.join(os.getcwd(), "assets", "branding"))
LOGO_HEADER_PATH = os.path.join(BRANDING_DIR, "logo-header.png")
LOGO_WATERMARK_PATH = os.path.join(BRANDING_DIR, "logo-watermark-faint.png")
LOGO_HEADER_ASPECT = 900 / 323  # width / height of the source header lockup

COLOR_PAPER = HexColor("#FBF7EF")
COLOR_INK = HexColor("#2B2620")
COLOR_INK_SOFT = HexColor("#6B6255")
COLOR_ORANGE = HexColor("#D9691F")
COLOR_ORANGE_DEEP = HexColor("#B8531A")
COLOR_CHARCOAL = HexColor("#2E2C2B")
COLOR_RULE = HexColor("#DDD2BC")
COLOR_ROW_TINT = HexColor("#F7EEDD")
COLOR_PENDING = HexColor("#B8531A")
COLOR_PAID = HexColor("#3F7D58")
COLOR_PENDING_FILL = HexColor("#F6E9DC")
COLOR_PAID_FILL = HexColor("#E6EFE9")

# Per-document copy/color config for the invoice vs. the receipt.
DOCUMENT_KINDS = {
    "invoice": {
        "label": "Invoice",
        "stamp_lines": ("Pending", "Payment"),
        "stamp_color": COLOR_PENDING,
        "cut_text": "HOLD FOR PAYMENT REVIEW",
        "note_text": (
            "Thanks for your order! We've received your proof of transfer and it's being "
            "reviewed. Once we confirm the payment has landed, we'll email you an official "
            "<b>Receipt</b> and your order moves to fulfilment."
        ),
        "note_border": COLOR_ORANGE,
        "note_fill": COLOR_PENDING_FILL,
        "total_label": "Total",
    },
    "receipt": {
        "label": "Receipt",
        "stamp_lines": ("Payment", "Confirmed"),
        "stamp_color": COLOR_PAID,
        "cut_text": "PAYMENT VERIFIED",
        "note_text": (
            "Payment received and confirmed \u2014 thank you for shopping with us! This "
            "receipt is your official proof of payment for order <b>#{order_id}</b>. Your "
            "order is now moving to fulfilment."
        ),
        "note_border": COLOR_PAID,
        "note_fill": COLOR_PAID_FILL,
        "total_label": "Total Paid",
    },
}


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


def _draw_paper_background(c, width, height):
    """Fill the page with the warm paper tone instead of stark white."""
    c.setFillColor(COLOR_PAPER)
    c.rect(0, 0, width, height, stroke=0, fill=1)


def _draw_watermark(c, width, height):
    """Faint, rotated circular badge centered behind the page content."""
    if not os.path.exists(LOGO_WATERMARK_PATH):
        return
    wm_w, wm_h = 100 * mm, 98 * mm
    c.saveState()
    c.translate(width / 2, height / 2)
    c.rotate(-8)
    c.drawImage(LOGO_WATERMARK_PATH, -wm_w / 2, -wm_h / 2, wm_w, wm_h, mask="auto")
    c.restoreState()


def _draw_header(c, order, top_y, kind_cfg):
    """Logo top-left, doc type + order meta top-right, charcoal rule beneath."""
    if os.path.exists(LOGO_HEADER_PATH):
        logo_h = 16 * mm
        logo_w = logo_h * LOGO_HEADER_ASPECT
        c.drawImage(LOGO_HEADER_PATH, 20 * mm, top_y - logo_h, logo_w, logo_h, mask="auto")

    c.setFillColor(COLOR_CHARCOAL)
    c.setFont("Times-Bold", 20)
    c.drawRightString(190 * mm, top_y - 6 * mm, kind_cfg["label"])

    c.setFillColor(COLOR_INK_SOFT)
    c.setFont("Courier", 8.5)
    c.drawRightString(190 * mm, top_y - 12 * mm, f"ORDER #{order.id}")
    c.drawRightString(190 * mm, top_y - 16 * mm, datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"))

    rule_y = top_y - 20 * mm
    c.setStrokeColor(COLOR_CHARCOAL)
    c.setLineWidth(1.4)
    c.line(20 * mm, rule_y, 190 * mm, rule_y)
    return rule_y


def _draw_stamp(c, top_y, kind_cfg):
    """Rotated circular stamp (Pending Payment / Payment Confirmed)."""
    cx, cy = 173 * mm, top_y - 34 * mm
    r = 17 * mm
    color = kind_cfg["stamp_color"]
    line1, line2 = kind_cfg["stamp_lines"]

    c.saveState()
    c.translate(cx, cy)
    c.rotate(-11)
    c.setStrokeColor(color)
    c.setLineWidth(1.6)
    c.circle(0, 0, r, stroke=1, fill=0)
    c.setLineWidth(0.7)
    c.circle(0, 0, r - 2 * mm, stroke=1, fill=0)
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(0, 2 * mm, line1.upper())
    c.drawCentredString(0, -3.5 * mm, line2.upper())
    c.restoreState()


def _draw_info_grid(c, order, y):
    """Deliver To / Contact Phone, two columns."""
    col1_x, col2_x = 20 * mm, 105 * mm

    c.setFillColor(COLOR_ORANGE_DEEP)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(col1_x, y, "DELIVER TO")
    c.drawString(col2_x, y, "CONTACT PHONE")

    c.setFillColor(COLOR_INK)
    c.setFont("Helvetica", 9.5)
    address = getattr(order, "delivery_address", "") or "N/A"
    phone = getattr(order, "contact_phone", "") or "N/A"
    c.drawString(col1_x, y - 5.5 * mm, address[:48])
    c.drawString(col2_x, y - 5.5 * mm, phone)

    return y - 14 * mm


def _draw_items_table(c, order, y, width, height):
    """Monospace, till-style line items table with a charcoal header row."""
    col_item_x, col_qty_x, col_price_x, col_sub_x = 22 * mm, 130 * mm, 155 * mm, 188 * mm
    row_h = 7 * mm

    def draw_header_row(y):
        c.setFillColor(COLOR_CHARCOAL)
        c.rect(20 * mm, y - row_h, 170 * mm, row_h, stroke=0, fill=1)
        c.setFillColor(COLOR_PAPER)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(col_item_x, y - row_h + 2.3 * mm, "ITEM")
        c.drawRightString(col_qty_x, y - row_h + 2.3 * mm, "QTY")
        c.drawRightString(col_price_x, y - row_h + 2.3 * mm, "PRICE")
        c.drawRightString(col_sub_x, y - row_h + 2.3 * mm, "SUBTOTAL")
        return y - row_h

    y = draw_header_row(y)
    c.setFont("Courier", 9)

    line_items, total = _order_line_items(order)
    for idx, (name, qty, price, subtotal) in enumerate(line_items):
        if y < 45 * mm:
            c.showPage()
            _draw_paper_background(c, width, height)
            _draw_watermark(c, width, height)
            y = height - 25 * mm
            y = draw_header_row(y)
            c.setFont("Courier", 9)

        if idx % 2 == 1:
            c.setFillColor(COLOR_ROW_TINT)
            c.rect(20 * mm, y - row_h, 170 * mm, row_h, stroke=0, fill=1)

        c.setFillColor(COLOR_INK)
        c.drawString(col_item_x, y - row_h + 2.3 * mm, name[:40])
        c.drawRightString(col_qty_x, y - row_h + 2.3 * mm, str(qty))
        c.drawRightString(col_price_x, y - row_h + 2.3 * mm, f"{price:,.2f}")
        c.drawRightString(col_sub_x, y - row_h + 2.3 * mm, f"{subtotal:,.2f}")

        c.setStrokeColor(COLOR_RULE)
        c.setDash(1, 2)
        c.setLineWidth(0.5)
        c.line(20 * mm, y - row_h, 190 * mm, y - row_h)
        c.setDash()
        y -= row_h

    return y, total


def _draw_totals(c, y, total, kind_cfg):
    """Right-aligned, stacked block (small caps label, then the big amount)
    -- stacking avoids any label/amount collision regardless of text length."""
    x_value = 188 * mm
    y -= 9 * mm

    c.setStrokeColor(COLOR_CHARCOAL)
    c.setLineWidth(1.2)
    c.line(120 * mm, y + 4 * mm, x_value, y + 4 * mm)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(COLOR_INK_SOFT)
    c.drawRightString(x_value, y, kind_cfg["total_label"].upper())

    y -= 6.5 * mm
    c.setFont("Courier-Bold", 15)
    c.setFillColor(COLOR_CHARCOAL)
    c.drawRightString(x_value, y, f"NGN {total:,.2f}")
    return y


def _draw_cut_divider(c, y, text):
    left_x, right_x = 20 * mm, 190 * mm
    mid = (left_x + right_x) / 2
    text_w = c.stringWidth(text, "Helvetica", 7.5)
    gap = 3 * mm

    c.setStrokeColor(COLOR_RULE)
    c.setDash(1, 2)
    c.setLineWidth(0.8)
    c.line(left_x, y, mid - text_w / 2 - gap, y)
    c.line(mid + text_w / 2 + gap, y, right_x, y)
    c.setDash()

    c.setFillColor(COLOR_INK_SOFT)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(mid, y - 2.6, text)
    return y - 10 * mm


def _draw_note_box(c, y, text, fill_color, border_color):
    x, box_width = 20 * mm, 170 * mm
    style = ParagraphStyle(name="note", fontName="Helvetica", fontSize=8.5, leading=12.5, textColor=COLOR_INK)
    para = Paragraph(text, style)
    _, text_h = para.wrap(box_width - 10 * mm, 40 * mm)
    box_h = text_h + 6 * mm

    c.setFillColor(fill_color)
    c.rect(x, y - box_h, box_width, box_h, stroke=0, fill=1)
    c.setFillColor(border_color)
    c.rect(x, y - box_h, 1.2 * mm, box_h, stroke=0, fill=1)
    para.drawOn(c, x + 6 * mm, y - box_h + 3 * mm)
    return y - box_h


def _draw_footer(c, y):
    """Thank-you line, Visit Us / Reach Us / Shop Online columns, baseline."""
    c.setFont("Times-Italic", 11)
    c.setFillColor(COLOR_ORANGE_DEEP)
    c.drawCentredString(105 * mm, y, "Thank you for shopping with C_Express Mini-Mart")

    y -= 6 * mm
    c.setStrokeColor(COLOR_RULE)
    c.setLineWidth(0.6)
    c.line(20 * mm, y, 190 * mm, y)
    y -= 6 * mm

    columns = [
        ("VISIT US", ["14B Allen Avenue", "Ikeja, Lagos"]),
        ("REACH US", ["+234 803 555 0199", "hello@cexpressminimart.ng"]),
        ("SHOP ONLINE", ["cexpressminimart.ng", "@cexpressminimart"]),
    ]
    label_y = y
    for (label, lines), cx in zip(columns, (45 * mm, 105 * mm, 165 * mm)):
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(COLOR_ORANGE_DEEP)
        c.drawCentredString(cx, label_y, label)
        c.setFont("Helvetica", 8)
        c.setFillColor(COLOR_INK)
        line_y = label_y - 4.5 * mm
        for line in lines:
            c.drawCentredString(cx, line_y, line)
            line_y -= 4 * mm

    y = label_y - 16 * mm
    c.setStrokeColor(COLOR_RULE)
    c.line(20 * mm, y, 190 * mm, y)
    y -= 5 * mm
    c.setFont("Helvetica", 7.5)
    c.setFillColor(COLOR_INK_SOFT)
    c.drawCentredString(105 * mm, y, "We'd love to have you back \u2014 patronize us again!")


def _render_pdf_document(disk_path, order, kind):
    """
    Shared, branded PDF layout used for both the invoice and the receipt --
    same order details and line items, different heading/stamp/note copy so
    the two documents are visually distinguishable at a glance.

    `kind` is "invoice" or "receipt" (see DOCUMENT_KINDS).
    Requires reportlab (`pip install reportlab`).
    """
    cfg = DOCUMENT_KINDS[kind]
    c = canvas.Canvas(disk_path, pagesize=A4)
    width, height = A4

    _draw_paper_background(c, width, height)
    _draw_watermark(c, width, height)

    top_y = height - 22 * mm
    rule_y = _draw_header(c, order, top_y, cfg)
    _draw_stamp(c, top_y, cfg)

    y = _draw_info_grid(c, order, rule_y - 10 * mm)
    y, total = _draw_items_table(c, order, y, width, height)
    y = _draw_totals(c, y, total, cfg)

    y -= 4 * mm
    y = _draw_cut_divider(c, y, cfg["cut_text"])

    note_text = cfg["note_text"].format(order_id=order.id)
    y = _draw_note_box(c, y, note_text, cfg["note_fill"], cfg["note_border"])

    # Pin the footer near the true bottom of the page; if content ran too
    # long and would collide with it, start a fresh page for the footer.
    footer_y = 40 * mm
    if y < footer_y + 20 * mm:
        c.showPage()
        _draw_paper_background(c, width, height)
        _draw_watermark(c, width, height)
    _draw_footer(c, footer_y)

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

    _render_pdf_document(disk_path, order, kind="invoice")

    return f"/uploads/{INVOICES_SUBDIR}/{invoice_filename}"


def _generate_receipt(order):
    """
    Generate the second document, sent only once the owner has confirmed
    the transfer landed. Returns its public URL.
    """
    _ensure_upload_dirs()
    receipt_filename = f"receipt_{order.id}.pdf"
    disk_path = os.path.join(UPLOAD_FOLDER, RECEIPTS_SUBDIR, receipt_filename)

    _render_pdf_document(disk_path, order, kind="receipt")

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

        user = UserRepo.get(secure_user_id)
        if not user:
            return jsonify({"message": "user for order not found"}), 404
        send_order_confirmation_email(order, user)
        send_owner_order_email(order)
    except Exception as e:
        current_app.logger.error(f"Failed to generate invoice for order {order.id}: {e}")
    return jsonify(order.to_dict()), 201

@app_views.route('/orders/<order_id>/confirm-payment', methods=['PUT'])
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

        user = order.user
        if not user:
            return jsonify({"message": "user does not exist"}), 404

        OrderRepo.update_receipt_url(order_id, receipt_url)
        send_receipt_email(order, user)
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
