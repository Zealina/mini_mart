#!/usr/bin/env python3
"""Category model"""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class Category(Base, BaseModel):
    """Manage categories"""
    __tablename__ = "categories"

    name = Column(String(128), nullable=False)
    parent_id = Column(String(36), ForeignKey("categories.id"), nullable=True)

    parent = relationship("Category", remote_side="Category.id", backref="subcategories")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"
