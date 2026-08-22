import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


BREVO_API_KEY = os.getenv("BREVO_API_KEY")
MAIL_FROM = os.getenv("MAIL_FROM")
OWNER_EMAIL = os.getenv("OWNER_EMAIL")

LOGO_URL = os.getenv(
    "LOGO_URL",
    "https://localhost/uploads/logo.png"
)

WEBSITE_URL = os.getenv("WEBSITE_URL")

STORE_NAME = "C_Express Minimart"


def send_email(to_email, subject, html_content):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    sender = sib_api_v3_sdk.SendSmtpEmailSender(
        email=MAIL_FROM,
        name=STORE_NAME
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        sender=sender,
        to=[{"email": to_email}],
        subject=subject,
        html_content=html_content
    )

    try:
        api_instance.send_transac_email(email)
        return True

    except ApiException as e:
        print(f"Email error: {e}")
        return False


def email_template(content):
    """
    Common C_Express Minimart email layout.
    """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>{STORE_NAME}</title>
    </head>

    <body style="
        margin: 0;
        padding: 0;
        background-color: #f4f4f4;
        font-family: Arial, Helvetica, sans-serif;
        color: #333333;
    ">

        <table width="100%" cellpadding="0" cellspacing="0"
               style="padding: 30px 10px;">

            <tr>
                <td align="center">

                    <table width="600" cellpadding="0" cellspacing="0"
                           style="
                               max-width: 600px;
                               width: 100%;
                               background: #ffffff;
                               border-radius: 8px;
                               overflow: hidden;
                           ">

                        <!-- HEADER -->
                        <tr>
                            <td align="center"
                                style="
                                    padding: 25px;
                                    background: #ffffff;
                                    border-bottom: 1px solid #eeeeee;
                                ">

                                <!-- LOGO -->
                                <img
                                    src="{LOGO_URL}"
                                    alt="{STORE_NAME}"
                                    style="
                                        max-width: 180px;
                                        max-height: 80px;
                                        display: block;
                                    "
                                >

                            </td>
                        </tr>

                        <!-- CONTENT -->
                        <tr>
                            <td style="padding: 35px 30px;">

                                {content}

                            </td>
                        </tr>

                        <!-- FOOTER -->
                        <tr>
                            <td align="center"
                                style="
                                    padding: 25px;
                                    background: #f8f8f8;
                                    color: #777777;
                                    font-size: 13px;
                                ">

                                <strong>{STORE_NAME}</strong>

                                <br><br>

                                <a href="{WEBSITE_URL}"
                                   style="
                                       color: #555555;
                                       text-decoration: none;
                                   ">
                                    Visit our website
                                </a>

                                <br><br>

                                Thank you for choosing {STORE_NAME}.

                            </td>
                        </tr>

                    </table>

                </td>
            </tr>

        </table>

    </body>
    </html>
    """


def send_welcome_email(user):
    first_name = getattr(user, "first_name", "there")

    content = f"""
        <h2 style="margin-top: 0;">
            Welcome to C_Express Minimart, {first_name}!
        </h2>

        <p>
            Thank you for creating an account with us.
        </p>

        <p>
            Your C_Express Minimart account has been successfully created.
            You can now browse our products, place orders, and keep track
            of your purchases.
        </p>

        <p>
            We are glad to have you shopping with us.
        </p>

        <p style="margin-top: 30px;">
            <a href="{WEBSITE_URL}"
               style="
                   display: inline-block;
                   padding: 12px 22px;
                   background: #222222;
                   color: #ffffff;
                   text-decoration: none;
                   border-radius: 5px;
               ">
                Start Shopping
            </a>
        </p>

        <p style="margin-top: 30px;">
            Regards,<br>
            <strong>C_Express Minimart</strong>
        </p>
    """

    return send_email(
        user.email,
        "Welcome to C_Express Minimart",
        email_template(content)
    )


def send_order_confirmation_email(order, user):

    customer_name = getattr(user, "first_name", "Customer")

    items_html = ""

    for item in order.items:

        item_total = item.price * item.quantity

        items_html += f"""
            <tr>
                <td style="
                    padding: 10px 5px;
                    border-bottom: 1px solid #eeeeee;
                ">
                    {item.product.name}
                </td>

                <td align="center"
                    style="
                        padding: 10px 5px;
                        border-bottom: 1px solid #eeeeee;
                    ">
                    {item.quantity}
                </td>

                <td align="right"
                    style="
                        padding: 10px 5px;
                        border-bottom: 1px solid #eeeeee;
                    ">
                    ₦{item.price:,.2f}
                </td>

                <td align="right"
                    style="
                        padding: 10px 5px;
                        border-bottom: 1px solid #eeeeee;
                    ">
                    ₦{item_total:,.2f}
                </td>
            </tr>
        """

    content = f"""
        <h2 style="margin-top: 0;">
            Thank you for your order, {customer_name}.
        </h2>

        <p>
            We have received your order and it is now being processed.
        </p>

        <div style="
            background: #f7f7f7;
            padding: 15px;
            border-radius: 5px;
            margin: 25px 0;
        ">
            <strong>Order #{order.id}</strong>
        </div>

        <h3>Order Summary</h3>

        <table width="100%"
               cellpadding="0"
               cellspacing="0"
               style="font-size: 14px;">

            <thead>
                <tr>
                    <th align="left"
                        style="padding: 10px 5px;">
                        Item
                    </th>

                    <th align="center"
                        style="padding: 10px 5px;">
                        Qty
                    </th>

                    <th align="right"
                        style="padding: 10px 5px;">
                        Price
                    </th>

                    <th align="right"
                        style="padding: 10px 5px;">
                        Total
                    </th>
                </tr>
            </thead>

            <tbody>
                {items_html}
            </tbody>

        </table>

        <table width="100%"
               style="margin-top: 20px;">

            <tr>
                <td align="right">
                    <strong>Total:</strong>
                </td>

                <td align="right"
                    width="120">
                    <strong>
                        ₦{order.total:,.2f}
                    </strong>
                </td>
            </tr>

        </table>

        <p style="margin-top: 30px;">
            We will notify you when there is an update regarding your order.
        </p>

        <p>
            If you have any questions about your order, please contact
            C_Express Minimart.
        </p>

        <p style="margin-top: 30px;">
            Regards,<br>
            <strong>C_Express Minimart</strong>
        </p>
    """

    return send_email(
        user.email,
        f"C_Express Minimart — Order #{order.id} Confirmed",
        email_template(content)
    )


def send_owner_order_email(order):

    if not OWNER_EMAIL:
        raise RuntimeError(
            "OWNER_EMAIL is not configured in the environment"
        )

    customer = order.user

    items_html = ""

    for item in order.items:

        item_total = item.price * item.quantity

        items_html += f"""
            <tr>
                <td style="padding: 10px 5px;
                           border-bottom: 1px solid #eeeeee;">
                    {item.product.name}
                </td>

                <td align="center"
                    style="padding: 10px 5px;
                           border-bottom: 1px solid #eeeeee;">
                    {item.quantity}
                </td>

                <td align="right"
                    style="padding: 10px 5px;
                           border-bottom: 1px solid #eeeeee;">
                    ₦{item.price:,.2f}
                </td>

                <td align="right"
                    style="padding: 10px 5px;
                           border-bottom: 1px solid #eeeeee;">
                    ₦{item_total:,.2f}
                </td>
            </tr>
        """

    content = f"""
        <h2 style="margin-top: 0;">
            New Order Received
        </h2>

        <p>
            A new order has been placed on C_Express Minimart
            and requires processing.
        </p>

        <div style="
            background: #f7f7f7;
            padding: 20px;
            border-radius: 5px;
            margin: 25px 0;
        ">

            <strong>Order #{order.id}</strong>

            <br><br>

            <strong>Customer:</strong>
            {customer.name}

            <br>

            <strong>Email:</strong>
            {customer.email}

        </div>

        <h3>Order Details</h3>

        <table width="100%"
               cellpadding="0"
               cellspacing="0"
               style="font-size: 14px;">

            <thead>
                <tr>
                    <th align="left"
                        style="padding: 10px 5px;">
                        Item
                    </th>

                    <th align="center"
                        style="padding: 10px 5px;">
                        Qty
                    </th>

                    <th align="right"
                        style="padding: 10px 5px;">
                        Price
                    </th>

                    <th align="right"
                        style="padding: 10px 5px;">
                        Total
                    </th>
                </tr>
            </thead>

            <tbody>
                {items_html}
            </tbody>

        </table>

        <div style="
            margin-top: 25px;
            padding: 15px;
            background: #f7f7f7;
            border-radius: 5px;
            text-align: right;
            font-size: 18px;
        ">

            <strong>
                Order Total: ₦{order.total:,.2f}
            </strong>

        </div>

        <p style="margin-top: 30px;">
            Please process this order.
        </p>

        <p>
            <strong>
                C_Express Minimart
            </strong>
        </p>
    """

    return send_email(
        OWNER_EMAIL,
        f"New C_Express Minimart Order #{order.id}",
        email_template(content)
    )
