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
    
    # ✅ STRICT DB COLUMNS
    delivery_address = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    gps_link = Column(String(255), nullable=True) # Kept in schema to avoid crashes, but ignored in UI

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
            
        # ✅ EXPLICIT ASSIGNMENT
        if "delivery_address" in kwargs:
            self.delivery_address = kwargs.get("delivery_address")
        if "contact_phone" in kwargs:
            self.contact_phone = kwargs.get("contact_phone")
            
        super().__init__(*args, **kwargs)

    def to_dict(self):
        """Override to_dict to explicitly include order items in JSON responses"""
        order_dict = super().to_dict()
        if hasattr(self, 'order_items') and self.order_items is not None:
            order_dict['order_items'] = [item.to_dict() for item in self.order_items]
        return order_dict
