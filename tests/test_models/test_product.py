#!/usr/bin/python3
"""
Contains the TestProductDocs classes
"""

from datetime import datetime
import inspect
import models
from models.product import Product
from models.base_model import BaseModel
import pep8
import unittest


class TestProductDocs(unittest.TestCase):
    """Tests to check the documentation and style of Product class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.product_f = inspect.getmembers(Product, inspect.isfunction)

    def test_pep8_conformance_product(self):
        """Test that models/product.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/product.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_product(self):
        """Test that tests/test_product.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['tests/test_product.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_product_module_docstring(self):
        """Test for the product.py module docstring"""
        from models import product
        self.assertIsNot(product.__doc__, None,
                         "product.py needs a docstring")
        self.assertTrue(len(product.__doc__) >= 1,
                        "product.py needs a docstring")

    def test_product_class_docstring(self):
        """Test for the City class docstring"""
        self.assertIsNot(Product.__doc__, None,
                         "Product class needs a docstring")
        self.assertTrue(len(Product.__doc__) >= 1,
                        "Product class needs a docstring")

    def test_product_func_docstrings(self):
        """Test for the presence of docstrings in Product methods"""
        for func in self.product_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestProduct(unittest.TestCase):
    """Test the Product class"""
    def setUp(self):
        """Setup method for tests of class methods"""
        self.product = Product()

    def test_is_subclass(self):
        """Test that Product is a subclass of BaseModel"""
        self.assertIsInstance(self.product, BaseModel)
        self.assertTrue(hasattr(self.product, "id"))
        self.assertTrue(hasattr(self.product, "created_at"))
        self.assertTrue(hasattr(self.product, "updated_at"))

    def test_to_dict_creates_dict(self):
        """test to_dict method creates a dictionary with proper attrs"""
        new_d = self.product.to_dict()
        self.assertEqual(type(new_d), dict)
        self.assertFalse("_sa_instance_state" in new_d)
        for attr in self.product.__dict__:
            if attr != "_sa_instance_state":
                self.assertTrue(attr in new_d)
        self.assertTrue("__class__" in new_d)

    def test_to_dict_values(self):
        """test that values in dict returned from to_dict are correct"""
        t_format = "%Y-%m-%dT%H:%M:%S.%f"
        new_d = self.product.to_dict()
        self.assertEqual(new_d["__class__"], "Product")
        self.assertEqual(type(new_d["created_at"]), str)
        self.assertEqual(type(new_d["updated_at"]), str)
        self.assertEqual(new_d["created_at"],
                         self.product.created_at.strftime(t_format))
        self.assertEqual(new_d["updated_at"],
                         self.product.updated_at.strftime(t_format))

    def test_str(self):
        """test that the str method has the correct output"""
        string = "[Product] ({}) {}".format(self.product.id,
                                            self.product.__dict__)
        self.assertEqual(string, str(self.product))


class TestProductAttributes(unittest.TestCase):
    """Tests for Product model attributes"""

    def setUp(self):
        """Create a new Product instance before each test"""
        self.product = Product(
            name="Bread",
            brand="Golden",
            description="Fresh wheat bread",
            category_id="12345",
            stock=10,
            package_size="1 loaf",
            price=500.0,
            currency="NGN",
            image_url="http://example.com/bread.jpg"
        )

    def test_name_attr(self):
        """Test Product has attribute name"""
        self.assertTrue(hasattr(self.product, "name"))
        self.assertEqual(self.product.name, "Bread")
        self.assertIsInstance(self.product.name, str)

    def test_brand_attr(self):
        """Test Product has attribute brand"""
        self.assertTrue(hasattr(self.product, "brand"))
        self.assertEqual(self.product.brand, "Golden")
        self.assertIsInstance(self.product.brand, str)

    def test_description_attr(self):
        """Test Product has attribute description"""
        self.assertTrue(hasattr(self.product, "description"))
        self.assertEqual(self.product.description, "Fresh wheat bread")
        self.assertIsInstance(self.product.description, str)

    def test_category_id_attr(self):
        """Test Product has attribute category_id"""
        self.assertTrue(hasattr(self.product, "category_id"))
        self.assertEqual(self.product.category_id, "12345")
        self.assertIsInstance(self.product.category_id, str)

    def test_stock_attr(self):
        """Test Product has attribute stock"""
        self.assertTrue(hasattr(self.product, "stock"))
        self.assertEqual(self.product.stock, 10)
        self.assertIsInstance(self.product.stock, int)

    def test_package_size_attr(self):
        """Test Product has attribute package_size"""
        self.assertTrue(hasattr(self.product, "package_size"))
        self.assertEqual(self.product.package_size, "1 loaf")
        self.assertIsInstance(self.product.package_size, str)

    def test_price_attr(self):
        """Test Product has attribute price"""
        self.assertTrue(hasattr(self.product, "price"))
        self.assertEqual(self.product.price, 500.0)
        self.assertIsInstance(self.product.price, float)

    def test_currency_default(self):
        """Test Product currency defaults to NGN"""
        prod = Product(name="Sugar", package_size="1kg", price=200.0)
        self.assertEqual(prod.currency, "NGN")

    def test_currency_override(self):
        """Test Product currency can be overridden"""
        prod = Product(name="Rice", package_size="5kg",
                       price=5000.0, currency="USD")
        self.assertEqual(prod.currency, "USD")

    def test_image_url_attr(self):
        """Test Product has attribute image_url"""
        self.assertTrue(hasattr(self.product, "image_url"))
        self.assertEqual(self.product.image_url,
                         "http://example.com/bread.jpg")
        self.assertIsInstance(self.product.image_url, str)

    def test_relationships_exist(self):
        """Test Product has relationships to category and order_items"""
        self.assertTrue(hasattr(self.product, "category"))
        self.assertTrue(hasattr(self.product, "order_items"))
