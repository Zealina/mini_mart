#!/usr/bin/env python3
"""Management of product items"""

from models import storage
from models.product import Product
from models.category import Category


class ProductRepo:
    """Repository class to manage product operations"""
    @classmethod
    def new_product(cls, **kwargs) -> Product:
        """Create and store a new product"""
        if not kwargs.get("name"):
            raise ValueError("Product name is not set")
        if not kwargs.get("price"):
            raise ValueError("Product price is not set")
        if not kwargs.get("volume"):
            raise ValueError("Prduct volume is not set")
        if not kwargs.get("category_id"):
            kwargs['category_id'] = None
        product = Product(
                name=kwargs['name'],
                volume=kwargs['volume'],
                category_id=kwargs['category_id'],
#               price=kwargs['price'],
                brand=None,
                description=None
            )
        product.save()
        return product

    @classmethod
    def get(cls, product_id: str) -> Product | None:
        """Retrieve a product by ID"""
        return storage.get(Product, product_id)

    @classmethod
    def all(cls) -> list[Product]:
        """Retrieve all products"""
        return storage.all(Product).values()

    @classmethod
    def update(cls, **kwargs) -> Product | None:
        """Update product details"""
        if not kwargs:
            return None
        product_id = kwargs.get("id")
        if not product_id:
            return None
        product = cls.get(product_id)
        if not product:
            return None
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        product.save()
        return product

    @classmethod
    def delete(cls, product_id: str) -> bool:
        """Delete a product"""
        product = cls.get(product_id)
        if not product:
            return False
        storage.delete(product)
        storage.save()
        return True

    def get_product_by_name(cls, name: str) -> Product | None:
        """Find a product by exact name"""
        return storage.session.query(Product).filter_by(name=name).first()

    def get_products_by_category(cls, category_id: str) -> list[Product]:
        """Retrieve all products in a given category"""
        return storage.session.query(Product).filter_by(category_id=category_id).all()

    def count_products_in_category(cls, category_id: str) -> int:
        """Count how many products belong to a category"""
        return storage.session.query(Product).filter_by(category_id=category_id).count()

    def move_product_to_category(cls, product_id: str, new_category_id: str) -> Product | None:
        """Change product's category"""
        product = cls.get_product_by_id(product_id)
        if not product:
            return None
        product.category_id = new_category_id
        storage.save()
        return product
