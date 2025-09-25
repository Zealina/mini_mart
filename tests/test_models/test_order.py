#!/usr/bin/python3
"""
Contains the TestOrderDocs classes
"""

from datetime import datetime
import inspect
import models
from models.order import Order
from models.base_model import BaseModel
import pep8
import unittest


class TestOrderDocs(unittest.TestCase):
    """Tests to check the documentation and style of Order class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.order_f = inspect.getmembers(Order, inspect.isfunction)

    def test_pep8_conformance_order(self):
        """Test that models/order.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/order.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_order(self):
        """Test that tests/test_order.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['tests/test_order.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_order_module_docstring(self):
        """Test for the order.py module docstring"""
        from models import order
        self.assertIsNot(order.__doc__, None,
                         "order.py needs a docstring")
        self.assertTrue(len(order.__doc__) >= 1,
                        "order.py needs a docstring")

    def test_order_class_docstring(self):
        """Test for the City class docstring"""
        self.assertIsNot(Order.__doc__, None,
                         "Order class needs a docstring")
        self.assertTrue(len(Order.__doc__) >= 1,
                        "Order class needs a docstring")

    def test_order_func_docstrings(self):
        """Test for the presence of docstrings in Order methods"""
        for func in self.order_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestOrder(unittest.TestCase):
    """Test the Order class"""
    def setUp(self):
        """Setup method for tests of class methods"""
        self.order = Order()

    def test_is_subclass(self):
        """Test that Order is a subclass of BaseModel"""
        self.assertIsInstance(self.order, BaseModel)
        self.assertTrue(hasattr(self.order, "id"))
        self.assertTrue(hasattr(self.order, "created_at"))
        self.assertTrue(hasattr(self.order, "updated_at"))

    def test_completed_attr(self):
        """Test that Order has attr completed and its 0"""
        self.assertTrue(hasattr(self.order, "completed"))
        self.assertEqual(self.order.completed, 0)

    def test_user_id_attr(self):
        """Test that Order has attr user_id and its 0"""
        self.assertTrue(hasattr(self.order, "user_id"))
        self.assertEqual(self.order.user_id, None)

    def test_to_dict_creates_dict(self):
        """test to_dict method creates a dictionary with proper attrs"""
        new_d = self.order.to_dict()
        self.assertEqual(type(new_d), dict)
        self.assertFalse("_sa_instance_state" in new_d)
        for attr in self.order.__dict__:
            if attr != "_sa_instance_state":
                self.assertTrue(attr in new_d)
        self.assertTrue("__class__" in new_d)

    def test_to_dict_values(self):
        """test that values in dict returned from to_dict are correct"""
        t_format = "%Y-%m-%dT%H:%M:%S.%f"
        new_d = self.order.to_dict()
        self.assertEqual(new_d["__class__"], "Order")
        self.assertEqual(type(new_d["created_at"]), str)
        self.assertEqual(type(new_d["updated_at"]), str)
        self.assertEqual(new_d["created_at"],
                         self.order.created_at.strftime(t_format))
        self.assertEqual(new_d["updated_at"],
                         self.order.updated_at.strftime(t_format))

    def test_str(self):
        """test that the str method has the correct output"""
        string = "[Order] ({}) {}".format(self.order.id, self.order.__dict__)
        self.assertEqual(string, str(self.order))

    def test_relationships(self):
        """Test that relationships to user and order_items are maintained"""
        self.assertTrue(hasattr(self.order, "user"))
        self.assertTrue(hasattr(self.order, "order_items"))
