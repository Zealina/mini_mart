#!/usr/bin/env python3
"""Management of product items"""

from models import storage
from models.product import Product
from models.category import Category


class ProductRepo:
    """Repository class to manage product operations"""

    @classmethod
    def new(cls, **kwargs) -> Product:
        """Create and store a new product"""
        if not kwargs.get("name"):
            raise ValueError("Product name is required")
        if not kwargs.get("price"):
            raise ValueError("Product price is required")

        product = Product(
            name=kwargs["name"],
            price=kwargs["price"],
            package_size=kwargs.get("package_size"),
            brand=kwargs.get("brand"),
            description=kwargs.get("description"),
            category_id=kwargs.get("category_id"),
            stock=kwargs.get("stock", 0),
            currency=kwargs.get("currency", "NGN"),
            image_url=kwargs.get("image_url")
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
        return storage.all(Product)

    @classmethod
    def update(cls, product_id, **kwargs) -> Product | None:
        """Update product details"""
        if not kwargs or not product_id:
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

    @classmethod
    def get_product_by_name(cls, name: str) -> Product | None:
        """Find a product by exact name"""
        return storage.get_by_attr(Product, name=name)

    @classmethod
    def get_products_by_category(cls, category_id: str) -> list[Product]:
        """Retrieve all products in a given category"""
        category = storage.get(Category, category_id)
        if not category:
            return False
        return storage.all_by_attr(Product, category_id=category_id)

    @classmethod
    def move_product_to_category(cls, product_id: str, new_category_id: str) -> Product | None:
        """Change product's category"""
        product = cls.get(product_id)
        if not product:
            return None
        product.category_id = new_category_id
        storage.save()
        return product
