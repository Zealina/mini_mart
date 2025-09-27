#!/usr/bin/env python3
"""Extended seed script for the Mini Mart database"""

from models import storage
from models.user import User
from models.category import Category
from models.product import Product
from models.order import Order
from models.order_item import OrderItem


def seed():
    # ---- USERS ----
    users = [
        User(
            first_name="Alice",
            last_name="Johnson",
            email="alice@example.com",
            phone_number="08010000001",
            whatsapp_number="08010000001",
            address="12 Market Street, Lagos",
            password="password123",
            is_admin=True
        ),
        User(
            first_name="Bob",
            last_name="Smith",
            email="bob@example.com",
            phone_number="08010000002",
            whatsapp_number="08010000002",
            address="34 Broad Road, Abuja",
            password="securepass",
            is_admin=False
        ),
        User(
            first_name="Clara",
            last_name="Ibrahim",
            email="clara@example.com",
            phone_number="08010000003",
            whatsapp_number="08010000003",
            address="15 Unity Close, Kano",
            password="mypassword",
            is_admin=False
        ),
        User(
            first_name="David",
            last_name="Okafor",
            email="david@example.com",
            phone_number="08010000004",
            whatsapp_number="08010000004",
            address="8 Festac Avenue, Enugu",
            password="letmein",
            is_admin=False
        ),
        User(
            first_name="Evelyn",
            last_name="Adams",
            email="evelyn@example.com",
            phone_number="08010000005",
            whatsapp_number="08010000005",
            address="22 Palm Grove, Ibadan",
            password="admin123",
            is_admin=True
        )
    ]

    # ---- CATEGORIES ----
    categories = {
        "food": Category(name="Food", description="All kinds of food items"),
        "drinks": Category(name="Drinks", description="Soft drinks, juices, water"),
        "household": Category(name="Household", description="Household essentials"),
        "snacks": Category(name="Snacks", description="Biscuits, chips, chocolates"),
        "electronics": Category(name="Electronics", description="Basic gadgets and accessories"),
        "personal": Category(name="Personal Care", description="Toiletries and personal care products"),
    }

    # ---- PRODUCTS ----
    products = [
        Product(name="Bag of Rice", brand="Royal Stallion",
                description="50kg bag of premium rice", category=categories["food"],
                stock=20, package_size="50kg", price=25000.0, currency="NGN", image_url=""),
        Product(name="Beans", brand="Honey Beans",
                description="5kg bag of honey beans", category=categories["food"],
                stock=30, package_size="5kg", price=5000.0, currency="NGN", image_url=""),
        Product(name="Coca-Cola", brand="Coca-Cola",
                description="50cl plastic bottle", category=categories["drinks"],
                stock=100, package_size="50cl", price=150.0, currency="NGN", image_url=""),
        Product(name="Pepsi", brand="Pepsi",
                description="50cl plastic bottle", category=categories["drinks"],
                stock=90, package_size="50cl", price=140.0, currency="NGN", image_url=""),
        Product(name="Detergent Powder", brand="Ariel",
                description="2kg pack of washing detergent", category=categories["household"],
                stock=40, package_size="2kg", price=2000.0, currency="NGN", image_url=""),
        Product(name="Toilet Paper", brand="Softy",
                description="Pack of 12 rolls", category=categories["household"],
                stock=60, package_size="12 rolls", price=1800.0, currency="NGN", image_url=""),
        Product(name="Potato Chips", brand="Pringles",
                description="Sour cream & onion flavor", category=categories["snacks"],
                stock=50, package_size="150g", price=900.0, currency="NGN", image_url=""),
        Product(name="Chocolate Bar", brand="Cadbury",
                description="Dairy Milk chocolate bar", category=categories["snacks"],
                stock=70, package_size="50g", price=500.0, currency="NGN", image_url=""),
        Product(name="Earphones", brand="Techie",
                description="Wired 3.5mm earphones", category=categories["electronics"],
                stock=25, package_size="1 pair", price=3500.0, currency="NGN", image_url=""),
        Product(name="Phone Charger", brand="FastCharge",
                description="USB fast charging adapter", category=categories["electronics"],
                stock=15, package_size="1 unit", price=5000.0, currency="NGN", image_url=""),
        Product(name="Toothpaste", brand="Colgate",
                description="Fresh Mint 120g tube", category=categories["personal"],
                stock=45, package_size="120g", price=800.0, currency="NGN", image_url=""),
        Product(name="Body Lotion", brand="Nivea",
                description="400ml moisturizing lotion", category=categories["personal"],
                stock=35, package_size="400ml", price=2500.0, currency="NGN", image_url="")
    ]

    # ---- ORDERS ----
    orders = [
        Order(user=users[0], completed=0),
        Order(user=users[1], completed=1),
        Order(user=users[2], completed=0),
        Order(user=users[3], completed=1),
        Order(user=users[4], completed=0),
    ]

    # ---- ORDER ITEMS ----
    order_items = [
        OrderItem(order=orders[0], product=products[0], quantity=2),  # Alice buys rice
        OrderItem(order=orders[0], product=products[2], quantity=5),  # Alice buys coke
        OrderItem(order=orders[1], product=products[4], quantity=3),  # Bob buys detergent
        OrderItem(order=orders[1], product=products[6], quantity=2),  # Bob buys chips
        OrderItem(order=orders[2], product=products[8], quantity=1),  # Clara buys earphones
        OrderItem(order=orders[2], product=products[10], quantity=2), # Clara buys toothpaste
        OrderItem(order=orders[3], product=products[1], quantity=1),  # David buys beans
        OrderItem(order=orders[3], product=products[11], quantity=1), # David buys lotion
        OrderItem(order=orders[4], product=products[3], quantity=4),  # Evelyn buys pepsi
        OrderItem(order=orders[4], product=products[7], quantity=6),  # Evelyn buys chocolate
    ]

    # ---- ADD TO STORAGE ----
    all_objects = users + list(categories.values()) + products + orders + order_items
    for obj in all_objects:
        obj.save()
    print("✅ Database seeded with extended sample data!")


if __name__ == "__main__":
    seed()
