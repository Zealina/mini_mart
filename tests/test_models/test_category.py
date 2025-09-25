#!/usr/bin/python3
"""
Contains the TestCategoryDocs classes
"""

from datetime import datetime
import inspect
import models
from models.category import Category
from models.base_model import BaseModel
import pep8
import unittest


class TestCategoryDocs(unittest.TestCase):
    """Tests to check the documentation and style of Category class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.category_f = inspect.getmembers(Category, inspect.isfunction)

    def test_pep8_conformance_category(self):
        """Test that models/category.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/category.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_category(self):
        """Test that tests/test_category.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['tests/test_category.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_category_module_docstring(self):
        """Test for the category.py module docstring"""
        from models import category
        self.assertIsNot(category.__doc__, None,
                         "category.py needs a docstring")
        self.assertTrue(len(category.__doc__) >= 1,
                        "category.py needs a docstring")

    def test_category_class_docstring(self):
        """Test for the City class docstring"""
        self.assertIsNot(Category.__doc__, None,
                         "Category class needs a docstring")
        self.assertTrue(len(Category.__doc__) >= 1,
                        "Category class needs a docstring")

    def test_category_func_docstrings(self):
        """Test for the presence of docstrings in Category methods"""
        for func in self.category_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestCategory(unittest.TestCase):
    """Test the Category class"""
    def setUp(self):
        """Setup method for tests of class methods"""
        self.category = Category()

    def test_is_subclass(self):
        """Test that Category is a subclass of BaseModel"""
        self.assertIsInstance(self.category, BaseModel)
        self.assertTrue(hasattr(self.category, "id"))
        self.assertTrue(hasattr(self.category, "created_at"))
        self.assertTrue(hasattr(self.category, "updated_at"))

    def test_name_attr(self):
        """Test that Category has attr name"""
        self.assertTrue(hasattr(self.category, "name"))
        self.assertEqual(self.category.name, None)
        self.category.name = "Category"
        self.assertEqual(self.category.name, "Category")

    def test_parent_id_attr(self):
        """Test that Category has attr parent_id"""
        self.assertTrue(hasattr(self.category, "parent_id"))
        self.assertEqual(self.category.parent_id, None)

    def test_to_dict_creates_dict(self):
        """test to_dict method creates a dictionary with proper attrs"""
        new_d = self.category.to_dict()
        self.assertEqual(type(new_d), dict)
        self.assertFalse("_sa_instance_state" in new_d)
        for attr in self.category.__dict__:
            if attr != "_sa_instance_state":
                self.assertTrue(attr in new_d)
        self.assertTrue("__class__" in new_d)

    def test_to_dict_values(self):
        """test that values in dict returned from to_dict are correct"""
        t_format = "%Y-%m-%dT%H:%M:%S.%f"
        new_d = self.category.to_dict()
        self.assertEqual(new_d["__class__"], "Category")
        self.assertEqual(type(new_d["created_at"]), str)
        self.assertEqual(type(new_d["updated_at"]), str)
        self.assertEqual(new_d["created_at"],
                         self.category.created_at.strftime(t_format))
        self.assertEqual(new_d["updated_at"],
                         self.category.updated_at.strftime(t_format))

    def test_str(self):
        """test that the str method has the correct output"""
        string = "[Category] ({}) {}".format(self.category.id,
                                             self.category.__dict__)
        self.assertEqual(string, str(self.category))

    def test_relationships_exist(self):
        """Test Category has relationships to parents and products"""
        self.assertTrue(hasattr(self.category, "parent"))
        self.assertTrue(hasattr(self.category, "products"))
