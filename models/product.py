#!/usr/bin/env python3
"""Product Model"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class Product(BaseModel, Base):
    """Represents a product in the mini-mart"""

    __tablename__ = "products"

    name = Column(String(128), nullable=False)
    brand = Column(String(128), nullable=True)
    description = Column(String(1024), nullable=True)
    category_id = Column(String(36), ForeignKey("categories.id"),
                         nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    package_size = Column(String(64), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(8), default="NGN")

    image_url = Column(String(512), nullable=True)

    order_items = relationship(
        "OrderItem",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    category = relationship("Category", back_populates="products")

    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        if "currency" in kwargs:
            self.currency = kwargs.get("currency")
        else:
            self.currency = "NGN"
        super().__init__(*args, **kwargs)
