"""
Test script for email_service.py

These tests mock the Brevo (sib_api_v3_sdk) client, so no real API key,
network access, or emails are needed to run them.

Run with:
    python3 -m unittest test_email_service.py -v
"""

import os
import base64
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

# Set env vars BEFORE importing email_service, since the module reads
# them at import time.
os.environ.setdefault("BREVO_API_KEY", "test-api-key")
os.environ.setdefault("MAIL_FROM", "no-reply@cexpress.test")
os.environ.setdefault("OWNER_EMAIL", "owner@cexpress.test")
os.environ.setdefault("WEBSITE_URL", "https://cexpress.test")

import email_service  # noqa: E402


def make_user(**overrides):
    defaults = dict(
        first_name="Ada",
        name="Ada Obi",
        email="ada@example.com",
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def make_order(payment_proof_url=None, invoice_url=None, receipt_url=None):
    product1 = SimpleNamespace(name="Rice (5kg)", price=8500.00)
    product2 = SimpleNamespace(name="Cooking Oil (1L)", price=3200.50)

    item1 = SimpleNamespace(product=product1, quantity=2)
    item2 = SimpleNamespace(product=product2, quantity=1)

    return SimpleNamespace(
        id=1042,
        order_items=[item1, item2],
        total=product1.price * item1.quantity + product2.price * item2.quantity,
        user=make_user(),
        payment_proof_url=payment_proof_url,
        invoice_url=invoice_url,
        receipt_url=receipt_url,
    )


def make_temp_file(suffix=".pdf", content=b"fake-file-bytes"):
    """
    Creates a temp file under a local 'uploads' folder relative to the
    current working directory, and returns (url_path, real_path).

    This mirrors how the app stores paths in production: a URL-style
    path like '/uploads/x.pdf' that the code turns into a relative
    path ('uploads/x.pdf') by stripping the leading slash.
    """
    uploads_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    fd, real_path = tempfile.mkstemp(suffix=suffix, dir=uploads_dir)
    with os.fdopen(fd, "wb") as f:
        f.write(content)

    filename = os.path.basename(real_path)
    url_path = f"/uploads/{filename}"

    return url_path, real_path


class EmailServiceTestCase(unittest.TestCase):
    """
    Base class that patches sib_api_v3_sdk.TransactionalEmailsApi so
    tests never make real network calls.
    """

    def setUp(self):
        patcher = patch("email_service.sib_api_v3_sdk.TransactionalEmailsApi")
        self.mock_api_cls = patcher.start()
        self.addCleanup(patcher.stop)

        self.mock_api_instance = MagicMock()
        self.mock_api_cls.return_value = self.mock_api_instance


class TestSendEmail(EmailServiceTestCase):

    def test_send_email_success(self):
        result = email_service.send_email(
            "someone@example.com", "Subject", "<p>Hi</p>"
        )
        self.assertTrue(result)
        self.mock_api_instance.send_transac_email.assert_called_once()

    def test_send_email_api_exception_returns_false(self):
        self.mock_api_instance.send_transac_email.side_effect = (
            email_service.ApiException(status=400, reason="Bad Request")
        )
        result = email_service.send_email(
            "someone@example.com", "Subject", "<p>Hi</p>"
        )
        self.assertFalse(result)


class TestWelcomeEmail(EmailServiceTestCase):

    def test_send_welcome_email(self):
        user = make_user()
        result = email_service.send_welcome_email(user)
        self.assertTrue(result)

        call_args = self.mock_api_instance.send_transac_email.call_args[0][0]
        self.assertIn(user.email, [t["email"] for t in call_args.to])
        self.assertIn("Welcome", call_args.subject)
        self.assertIn(user.first_name, call_args.html_content)


class TestOrderConfirmationEmail(EmailServiceTestCase):

    def test_send_order_confirmation_email_no_invoice(self):
        order = make_order(invoice_url=None)
        user = order.user

        result = email_service.send_order_confirmation_email(order, user)
        self.assertTrue(result)

        call_args = self.mock_api_instance.send_transac_email.call_args[0][0]
        self.assertIn(str(order.id), call_args.subject)
        for item in order.order_items:
            self.assertIn(item.product.name, call_args.html_content)
        self.assertFalse(hasattr(call_args, "attachment") and call_args.attachment)

    def test_send_order_confirmation_email_with_invoice(self):
        url_path, real_path = make_temp_file(suffix=".pdf", content=b"invoice-bytes")
        try:
            order = make_order(invoice_url=url_path)
            user = order.user

            result = email_service.send_order_confirmation_email(order, user)
            self.assertTrue(result)

            call_args = self.mock_api_instance.send_transac_email.call_args[0][0]
            self.assertTrue(hasattr(call_args, "attachment"))
            self.assertEqual(len(call_args.attachment), 1)
            self.assertEqual(
                base64.b64decode(call_args.attachment[0].content), b"invoice-bytes"
            )
        finally:
            os.unlink(real_path)


class TestReceiptEmail(EmailServiceTestCase):

    def test_send_receipt_email_no_attachment(self):
        order = make_order(receipt_url=None)
        user = order.user

        result = email_service.send_receipt_email(order, user)
        self.assertTrue(result)

        call_args = self.mock_api_instance.send_transac_email.call_args[0][0]
        self.assertIn(str(order.id), call_args.subject)
        self.assertIn("Receipt", call_args.subject)
        for item in order.order_items:
            self.assertIn(item.product.name, call_args.html_content)
        self.assertIn(f"{order.total:,.2f}", call_args.html_content)
        self.assertFalse(hasattr(call_args, "attachment") and call_args.attachment)

    def test_send_receipt_email_with_attachment(self):
        url_path, real_path = make_temp_file(suffix=".pdf", content=b"receipt-bytes")
        try:
            order = make_order(receipt_url=url_path)
            user = order.user

            result = email_service.send_receipt_email(order, user)
            self.assertTrue(result)

            call_args = self.mock_api_instance.send_transac_email.call_args[0][0]
            self.assertTrue(hasattr(call_args, "attachment"))
            self.assertEqual(len(call_args.attachment), 1)
            self.assertEqual(
                base64.b64decode(call_args.attachment[0].content), b"receipt-bytes"
            )
            self.assertIn(str(order.id), call_args.attachment[0].name)
        finally:
            os.unlink(real_path)

    def test_send_receipt_email_missing_file_on_disk(self):
        order = make_order(receipt_url="/nonexistent/path/receipt.pdf")
        user = order.user

        result = email_service.send_receipt_email(order, user)
        self.assertTrue(result)

        call_args = self.mock_api_instance.send_transac_email.call_args[0][0]
        self.assertFalse(hasattr(call_args, "attachment") and call_args.attachment)


class TestOwnerOrderEmail(EmailServiceTestCase):

    def test_send_owner_order_email_with_payment_proof(self):
        url_path, real_path = make_temp_file(suffix=".png", content=b"proof-bytes")

        try:
            order = make_order(payment_proof_url=url_path)

            result = email_service.send_owner_order_email(order)
            self.assertTrue(result)

            call_args = self.mock_api_instance.send_transac_email.call_args[0][0]
            self.assertEqual(call_args.to[0]["email"], os.environ["OWNER_EMAIL"])
            self.assertIn(order.user.first_name, call_args.html_content)
            self.assertIn(order.user.email, call_args.html_content)
            self.assertIn("attached to this email", call_args.html_content)

            self.assertTrue(hasattr(call_args, "attachment"))
            self.assertEqual(len(call_args.attachment), 1)
            self.assertEqual(
                base64.b64decode(call_args.attachment[0].content), b"proof-bytes"
            )

        finally:
            os.unlink(real_path)

    def test_send_owner_order_email_without_payment_proof(self):
        order = make_order(payment_proof_url=None)

        result = email_service.send_owner_order_email(order)
        self.assertTrue(result)

        call_args = self.mock_api_instance.send_transac_email.call_args[0][0]
        self.assertIn("No payment proof was attached", call_args.html_content)

    def test_send_owner_order_email_raises_without_owner_email(self):
        order = make_order()
        with patch.object(email_service, "OWNER_EMAIL", None):
            with self.assertRaises(RuntimeError):
                email_service.send_owner_order_email(order)


class TestResetPasswordEmail(EmailServiceTestCase):

    def test_send_reset_password_email(self):
        user = make_user()
        token = "abc123token"

        result = email_service.send_reset_password_email(user, token)
        self.assertTrue(result)

        call_args = self.mock_api_instance.send_transac_email.call_args[0][0]
        self.assertEqual(call_args.to[0]["email"], user.email)
        self.assertIn("Reset", call_args.subject)
        expected_link = f"{email_service.WEBSITE_URL}/auth?token={token}"
        self.assertIn(expected_link, call_args.html_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
