#!/usr/bin/env python3
"""Product Model"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class Product(Base, BaseModel):
    """
    Represents a product in the mini-mart.

    Fields:
        name (str): Name of the product. Example: "Coca-Cola".
        brand (str): Brand of the product. Example: "Coca-Cola Company".
        description (str): A short overview of the product. Should include:
            - What the product is
            - Key features (flavor, material, special qualities)
            - Usage context (snack, cooking, household, etc.)
            
            E.g:
            "Golden Penny Spaghetti is made from 100% durum wheat, 
            cooks in under 10 minutes, and is perfect for preparing 
            both traditional and continental pasta dishes."

        category_id (str): Foreign key to Category table (e.g. "Beverages", "Snacks").
        stock (int): How many units are available in inventory.
        package_size (str): How the product is packaged, including measurement units.
            Examples: "500ml bottle", "1kg pack", "12-piece carton".
        price (float): Price of the product in the given currency.
        currency (str): Currency code for the price. Default: "NGN".
        image_url (str): URL pointing to the main image of the product.

    Relationships:
        order_items: OrderItem objects referencing this product.
        category: The Category this product belongs to.

    Example:
        Product(
            name="Pepsi",
            brand="PepsiCo",
            description="Refreshing carbonated soft drink with a bold taste. "
                        "Best served chilled.",
            category_id="beverages-uuid",
            stock=120,
            package_size="500ml bottle",
            price=250.0,
            currency="NGN",
            image_url="https://example.com/images/pepsi-500ml.jpg"
        )
    """

    __tablename__ = "products"

    name = Column(String(128), nullable=False)
    brand = Column(String(128), nullable=True)
    description = Column(String(1024), nullable=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
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

    def __repr__(self):
        return (
            f"<Product(id={self.id}, name='{self.name}', "
            f"stock={self.stock}, price={self.price}{self.currency})>"
        )
