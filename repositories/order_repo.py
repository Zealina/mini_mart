#!/usr/bin/env python3
"""Management of order items"""

from models import storage
from models.order import Order
from models.order_item import OrderItem
from models.product import Product

class OrderRepo:
    """Repository class to manage order operations"""
 
    @classmethod
    def new(cls, user_id: str, items: dict, address: str = None, phone: str = None) -> Order:
        """
        Create a new order with items.
        """
        if not items or not isinstance(items, dict):
            raise ValueError("Order items must be provided as a dict {product_id: quantity}")

        # ✅ EXPLICIT OBJECT CREATION - No Kwargs!
        order = Order(user_id=user_id, delivery_address=address, contact_phone=phone)
        order.save()
        storage.save()

        for product_id, quantity in items.items():
            product = storage.get(Product, product_id)
            if not product:
                raise ValueError(f"Product:{product_id} does not exist")
            new_item = OrderItem(order_id=order.id, product_id=product_id, quantity=quantity)
            new_item.save()

        storage.save()
        return order

    @classmethod
    def get(cls, order_id: str) -> Order | None:
        """Retrieve an order by ID"""
        return storage.get(Order, order_id)

    @classmethod
    def all(cls) -> list[Order]:
        """Retrieve all orders"""
        return storage.all(Order)

    @classmethod
    def delete(cls, order_id: str) -> bool:
        """Delete an order by ID (including its items)"""
        order = cls.get(order_id)
        if not order:
            return False
        storage.delete(order)
        storage.save()
        return True

    @classmethod
    def add_item(cls, order_id: str, product_id: str, quantity: int) -> OrderItem | None:
        """Add a product to an existing order"""
        order = cls.get(order_id)
        if not order:
            return None
        item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity)
        item.save()
        storage.save()
        return item

    @classmethod
    def remove_item(cls, order_id: str, product_id: str) -> bool:
        """Remove a product from an existing order"""
        order = cls.get(order_id)
        if not order:
            return False
        items = storage.get_by_attr(OrderItem, order_id=order_id, product_id=product_id)
        if not items:
            return False
        for item in items:
            storage.delete(item)
        storage.save()
        return True

    @classmethod
    def get_items(cls, order_id: str) -> list[OrderItem]:
        """Retrieve all items in a given order"""
        order =  storage.get(Order, order_id)
        return order.order_items