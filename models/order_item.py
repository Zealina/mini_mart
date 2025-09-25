#!/usr/bin/env python3
"""OrderItem Model"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class OrderItem(BaseModel, Base):
    """Association object between Order and Product, with order_item"""

    __tablename__ = "order_items"

    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        if "quantity" in kwargs:
            self.quantity = kwargs.get("quantity")
        else:
            self.quantity = 1
        super().__init__(*args, **kwargs)
