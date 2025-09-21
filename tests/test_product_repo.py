#!/usr/bin/env python3
import unittest
from repositories.product_repo import ProductRepo
from models.product import Product
from models import storage


class TestProductRepo(unittest.TestCase):
    product_id = None

    def test_1_fail_missing_fields(self):
        """Fail to create product without required fields"""
        with self.assertRaises(ValueError):
            ProductRepo.new(name="Coca-Cola")  # missing price & package_size

    def test_2_create_product(self):
        """Create a valid product"""
        product = ProductRepo.new(
            name="Coca-Cola",
            brand="Coca-Cola Company",
            description="Refreshing soft drink, best served chilled.",
            package_size="500ml bottle",
            price=250.0,
            stock=50,
            currency="NGN",
            image_url="https://example.com/images/coke-500ml.jpg",
        )
        self.__class__.product_id = product.id
        self.assertIsInstance(product, Product)
        print("Created product:", product)

    def test_3_get_product(self):
        """Retrieve product by ID"""
        product = ProductRepo.get(self.product_id)
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "Coca-Cola")
        print("Fetched product:", product)

    def test_4_get_by_name(self):
        """Retrieve product by name"""
        product = ProductRepo.get_product_by_name("Coca-Cola")
        self.assertIsNotNone(product)
        print("Fetched by name:", product)

    def test_5_update_product(self):
        """Update product fields"""
        product = ProductRepo.update(
            id=self.product_id,
            stock=200,
            price=300.0
        )
        self.assertEqual(product.stock, 200)
        self.assertEqual(product.price, 300.0)
        print("Updated product:", product)

    def test_7_delete_product(self):
        """Delete product"""
        success = ProductRepo.delete(self.product_id)
        self.assertTrue(success)
        product = ProductRepo.get(self.product_id)
        self.assertIsNone(product)
        print("Product deleted successfully")


if __name__ == "__main__":
    unittest.main()
