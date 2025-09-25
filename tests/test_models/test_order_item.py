#!/usr/bin/python3
"""
Contains the TestOrderItemDocs classes
"""

from datetime import datetime
import inspect
import models
from models.order_item import OrderItem
from models.base_model import BaseModel
import pep8
import unittest


class TestOrderItemDocs(unittest.TestCase):
    """Tests to check the documentation and style of OrderItem class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.order_item_f = inspect.getmembers(OrderItem, inspect.isfunction)

    def test_pep8_conformance_order_item(self):
        """Test that models/order_item.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/order_item.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_order_item(self):
        """Test that tests/test_order_item.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['tests/test_order_item.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_order_item_module_docstring(self):
        """Test for the order_item.py module docstring"""
        from models import order_item
        self.assertIsNot(order_item.__doc__, None,
                         "order_item.py needs a docstring")
        self.assertTrue(len(order_item.__doc__) >= 1,
                        "order_item.py needs a docstring")

    def test_order_item_class_docstring(self):
        """Test for the City class docstring"""
        self.assertIsNot(OrderItem.__doc__, None,
                         "OrderItem class needs a docstring")
        self.assertTrue(len(OrderItem.__doc__) >= 1,
                        "OrderItem class needs a docstring")

    def test_order_item_func_docstrings(self):
        """Test for the presence of docstrings in OrderItem methods"""
        for func in self.order_item_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestOrderItem(unittest.TestCase):
    """Test the OrderItem class"""
    def setUp(self):
        """Setup method for tests of class methods"""
        self.order_item = OrderItem()

    def test_is_subclass(self):
        """Test that OrderItem is a subclass of BaseModel"""
        self.assertIsInstance(self.order_item, BaseModel)
        self.assertTrue(hasattr(self.order_item, "id"))
        self.assertTrue(hasattr(self.order_item, "created_at"))
        self.assertTrue(hasattr(self.order_item, "updated_at"))

    def test_order_id_attr(self):
        """Test that OrderItem has attr order_id and its 0"""
        self.assertTrue(hasattr(self.order_item, "order_id"))
        self.assertEqual(self.order_item.order_id, None)

    def test_product_id_attr(self):
        """Test that OrderItem has attr product_id and its 0"""
        self.assertTrue(hasattr(self.order_item, "product_id"))
        self.assertEqual(self.order_item.product_id, None)

    def test_quantity_attr(self):
        """Test that OrderItem has attr quantity and its at least 1"""
        self.assertTrue(hasattr(self.order_item, "quantity"))
        self.assertEqual(self.order_item.quantity, 1)
        self.order_item.quantity += 298
        self.assertEqual(self.order_item.quantity, 299)

    def test_to_dict_creates_dict(self):
        """test to_dict method creates a dictionary with proper attrs"""
        new_d = self.order_item.to_dict()
        self.assertEqual(type(new_d), dict)
        self.assertFalse("_sa_instance_state" in new_d)
        for attr in self.order_item.__dict__:
            if attr != "_sa_instance_state":
                self.assertTrue(attr in new_d)
        self.assertTrue("__class__" in new_d)

    def test_to_dict_values(self):
        """test that values in dict returned from to_dict are correct"""
        t_format = "%Y-%m-%dT%H:%M:%S.%f"
        new_d = self.order_item.to_dict()
        self.assertEqual(new_d["__class__"], "OrderItem")
        self.assertEqual(type(new_d["created_at"]), str)
        self.assertEqual(type(new_d["updated_at"]), str)
        self.assertEqual(new_d["created_at"],
                         self.order_item.created_at.strftime(t_format))
        self.assertEqual(new_d["updated_at"],
                         self.order_item.updated_at.strftime(t_format))

    def test_str(self):
        """test that the str method has the correct output"""
        string = "[OrderItem] ({}) {}".format(self.order_item.id,
                                              self.order_item.__dict__)
        self.assertEqual(string, str(self.order_item))

    def test_relationships(self):
        """Test OrderItem relationship to order and product"""
        self.assertTrue(hasattr(self.order_item, "product"))
        self.assertTrue(hasattr(self.order_item, "order"))
