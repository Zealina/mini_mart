#!/usr/bin/env python3
"""Product Model"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class Product(Base, BaseModel):
    """Define a product and its properties"""

    __tablename__ = "products"

    name = Column(String(128), nullable=False)
    brand = Column(String(128), nullable=True)
    description = Column(String(1024), nullable=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    volume = Column(Integer, nullable=False)

    order_items = relationship(
        "OrderItem",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', volume='{self.volume}')>"
