#!/usr/bin/env python3
"""Management of order items"""

from models import storage
from models.order import Order
from models.order_item import OrderItem
from models.product import Product

class OrderRepo:
    """Repository class to manage order operations"""
 
    @classmethod
    def new(cls, user_id: str, items: dict, **kwargs) -> Order:
        if not items or not isinstance(items, dict):
            raise ValueError("Order items must be provided as a dict {product_id: quantity}")

        # ✅ VERIFY STOCK BEFORE CREATING ORDER
        for product_id, quantity in items.items():
            product = storage.get(Product, product_id)
            if not product:
                raise ValueError(f"Product not found.")
            if product.stock < quantity:
                raise ValueError(f"Insufficient stock for {product.name}. Only {product.stock} left.")

        # Create the order
        order = Order(user_id=user_id, **kwargs)
        order.save()
        storage.save()

        # Save order items AND deduct from warehouse stock
        for product_id, quantity in items.items():
            product = storage.get(Product, product_id)
            
            # ✅ DEDUCT THE STOCK
            product.stock -= quantity
            product.save()

            new_item = OrderItem(order_id=order.id, product_id=product_id, quantity=quantity)
            new_item.save()

        storage.save()
        return order

    @classmethod
    def get(cls, order_id: str) -> Order | None:
        return storage.get(Order, order_id)

    @classmethod
    def all(cls) -> list[Order]:
        return storage.all(Order)

    @classmethod
    def delete(cls, order_id: str) -> bool:
        order = cls.get(order_id)
        if not order:
            return False
            
        # ✅ RESTOCK IF CANCELLED BY ADMIN
        for item in order.order_items:
            product = storage.get(Product, item.product_id)
            if product: 
                product.stock += item.quantity
                product.save()

        storage.delete(order)
        storage.save()
        return True

    @classmethod
    def add_item(cls, order_id: str, product_id: str, quantity: int) -> OrderItem | None:
        order = cls.get(order_id)
        if not order:
            return None
        item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity)
        item.save()
        storage.save()
        return item

    @classmethod
    def remove_item(cls, order_id: str, product_id: str) -> bool:
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
        order = storage.get(Order, order_id)
        return order.order_items