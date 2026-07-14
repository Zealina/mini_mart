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
    gps_link = Column(String(255), nullable=True) 

    user = relationship("User", back_populates="orders")
    order_items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        # ✅ 1. Initialize BaseModel FIRST to prevent it from overwriting our custom kwargs
        super().__init__(*args, **kwargs)
        
        self.completed = kwargs.get("completed", 0)
        
        # ✅ 2. EXPLICIT ASSIGNMENT AFTER SUPER
        if "delivery_address" in kwargs:
            self.delivery_address = kwargs.get("delivery_address")
        if "contact_phone" in kwargs:
            self.contact_phone = kwargs.get("contact_phone")
        if "gps_link" in kwargs:
            self.gps_link = kwargs.get("gps_link")

    def to_dict(self):
        """Override to_dict to explicitly guarantee delivery details go to React"""
        order_dict = super().to_dict()
        
        # ✅ 3. FORCE THE DATA INTO THE JSON RESPONSE
        order_dict['delivery_address'] = getattr(self, 'delivery_address', None)
        order_dict['contact_phone'] = getattr(self, 'contact_phone', None)
        order_dict['gps_link'] = getattr(self, 'gps_link', None)
        
        if hasattr(self, 'order_items') and self.order_items is not None:
            order_dict['order_items'] = [item.to_dict() for item in self.order_items]
            
        return order_dict