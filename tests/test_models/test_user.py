#!/usr/bin/python3
"""
Contains the TestUserDocs classes
"""

from datetime import datetime
import inspect
import models
from models.user import User
from models.base_model import BaseModel
import pep8
import unittest


class TestUserDocs(unittest.TestCase):
    """Tests to check the documentation and style of User class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.user_f = inspect.getmembers(User, inspect.isfunction)

    def test_pep8_conformance_user(self):
        """Test that models/user.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/user.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_user(self):
        """Test that tests/test_user.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['tests/test_user.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_user_module_docstring(self):
        """Test for the user.py module docstring"""
        from models import user
        self.assertIsNot(user.__doc__, None,
                         "user.py needs a docstring")
        self.assertTrue(len(user.__doc__) >= 1,
                        "user.py needs a docstring")

    def test_user_class_docstring(self):
        """Test for the City class docstring"""
        self.assertIsNot(User.__doc__, None,
                         "User class needs a docstring")
        self.assertTrue(len(User.__doc__) >= 1,
                        "User class needs a docstring")

    def test_user_func_docstrings(self):
        """Test for the presence of docstrings in User methods"""
        for func in self.user_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestUser(unittest.TestCase):
    """Test the User class"""
    def setUp(self):
        """Setup method for tests of class methods"""
        self.user = User()
        self.password = "C_Express_mini_mart"

    def test_is_subclass(self):
        """Test that User is a subclass of BaseModel"""
        self.assertIsInstance(self.user, BaseModel)
        self.assertTrue(hasattr(self.user, "id"))
        self.assertTrue(hasattr(self.user, "created_at"))
        self.assertTrue(hasattr(self.user, "updated_at"))

    def test_email_attr(self):
        """Test that User has attr email, and it's None"""
        self.assertTrue(hasattr(self.user, "email"))
        self.assertEqual(self.user.email, None)

    def test_password_attr(self):
        """Test that User has attr password, and it's None"""
        self.assertTrue(hasattr(self.user, "password"))
        self.assertEqual(self.user.password, None)

    def test_first_name_attr(self):
        """Test that User has attr first_name, and it's None"""
        self.assertTrue(hasattr(self.user, "first_name"))
        self.assertEqual(self.user.first_name, None)

    def test_last_name_attr(self):
        """Test that User has attr last_name, and it's None"""
        self.assertTrue(hasattr(self.user, "last_name"))
        self.assertEqual(self.user.last_name, None)

    def test_to_dict_creates_dict(self):
        """test to_dict method creates a dictionary with proper attrs"""
        new_d = self.user.to_dict()
        self.assertEqual(type(new_d), dict)
        self.assertFalse("_sa_instance_state" in new_d)
        for attr in self.user.__dict__:
            if attr != "_sa_instance_state":
                self.assertTrue(attr in new_d)
        self.assertTrue("__class__" in new_d)

    def test_to_dict_values(self):
        """test that values in dict returned from to_dict are correct"""
        t_format = "%Y-%m-%dT%H:%M:%S.%f"
        new_d = self.user.to_dict()
        self.assertEqual(new_d["__class__"], "User")
        self.assertEqual(type(new_d["created_at"]), str)
        self.assertEqual(type(new_d["updated_at"]), str)
        self.assertEqual(new_d["created_at"],
                         self.user.created_at.strftime(t_format))
        self.assertEqual(new_d["updated_at"],
                         self.user.updated_at.strftime(t_format))

    def test_str(self):
        """test that the str method has the correct output"""
        string = "[User] ({}) {}".format(self.user.id, self.user.__dict__)
        self.assertEqual(string, str(self.user))

    def test_password_creation(self):
        """tests that the password is not stored normally"""
        self.user.password = self.password
        self.user.first_name = "C_Express"
        self.user.last_name = "Mini_Mart"
        self.user.email = "c_express@mini_mart.com"
        self.assertNotEqual(self.user.password, self.password)
        self.assertEqual(self.user.first_name, "C_Express")
        self.assertEqual(self.user.last_name, "Mini_Mart")
        self.assertEqual(self.user.email, "c_express@mini_mart.com")

    def test_check_password(self):
        """tests that the check pasword is accurate"""
        self.user.password = "C_Express_mini_mart"
        self.assertTrue(self.user.check_password(self.password))
        self.assertNotEqual(self.user.password, self.password)
