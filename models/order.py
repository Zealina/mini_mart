#!/usr/bin/env python3
"""Order Model"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class Order(BaseModel, Base):
    """Define an order and its properties"""

    __tablename__ = "orders"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    completed = Column(Integer, nullable=False, default=0)

    user = relationship("User", back_populates="orders")
    order_items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        if "completed" in kwargs:
            self.completed = kwargs.get("completed")
        else:
            self.completed = 0
        super().__init__(*args, **kwargs)
