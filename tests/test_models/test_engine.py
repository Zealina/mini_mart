#!/usr/bin/python3
"""
Contains the TestStorageDocs and TestStorage classes
"""

from datetime import datetime
import inspect
import pep8
import unittest
from models import Storage
from models import engine
from unittest.mock import patch, MagicMock
import os


class TestStorageDocs(unittest.TestCase):
    """Tests to check the documentation and style of Storage class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.s_f = inspect.getmembers(Storage, inspect.isfunction)

    def test_pep8_conformance_storage(self):
        """Test that models/engine/engine.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/engine/engine.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_storage(self):
        """Test tests/test_models/test_engine.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['tests/test_models/test_engine/\
test_engine.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_storage_module_docstring(self):
        """Test for the engine.py module docstring"""
        self.assertIsNot(storage.__doc__, None,
                         "engine.py needs a docstring")
        self.assertTrue(len(storage.__doc__) >= 1,
                        "engine.py needs a docstring")

    def test_storage_class_docstring(self):
        """Test for the Storage class docstring"""
        self.assertIsNot(Storage.__doc__, None,
                         "Storage class needs a docstring")
        self.assertTrue(len(Storage.__doc__) >= 1,
                        "Storage class needs a docstring")

    def test_s_func_docstrings(self):
        """Test for the presence of docstrings in Storage methods"""
        for func in self.s_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestStorage(unittest.TestCase):
    """Test suite for the Storage class"""

    def setUp(self):
        """Set up default environment values for use in tests"""
        self.dummy_env = {
            'MINI_MART_MYSQL_USER': 'u',
            'MINI_MART_MYSQL_PWD': 'p',
            'MINI_MART_MYSQL_HOST': 'localhost',
            'MINI_MART_MYSQL_DB': 'testdb',
            'MINI_MART_ENV': 'dev'
        }

    @patch.dict(os.environ, {}, clear=True)
    def test_init_missing_env_vars_raises(self):
        """Ensure Storage raises ValueError if any env var is missing"""
        with self.assertRaises(ValueError):
            engine.Storage()

    @patch.dict(os.environ, {
        'MINI_MART_MYSQL_USER': 'u',
        'MINI_MART_MYSQL_PWD': 'p',
        'MINI_MART_MYSQL_HOST': 'localhost',
        'MINI_MART_MYSQL_DB': 'testdb',
        'MINI_MART_ENV': 'dev'
    }, clear=True)
    @patch("models.engine.create_engine")
    def test_init_engine_called(self, mock_engine):
        """Ensure create_engine is called with the correct DB URL"""
        store = engine.Storage()
        mock_engine.assert_called_once_with("mysql+pymysql://u:p@localhost/testdb")
        self.assertIsInstance(store, engine.Storage)

    @patch.dict(os.environ, {
        'MINI_MART_MYSQL_USER': 'u',
        'MINI_MART_MYSQL_PWD': 'p',
        'MINI_MART_MYSQL_HOST': 'localhost',
        'MINI_MART_MYSQL_DB': 'testdb',
        'MINI_MART_ENV': 'test'
    }, clear=True)
    @patch("models.engine.create_engine")
    @patch("models.engine.Base.metadata.drop_all")
    def test_init_env_test_drops_all(self, mock_drop, mock_engine):
        """Ensure ENV=test triggers metadata.drop_all on init"""
        engine.Storage()
        mock_drop.assert_called_once()

    def make_storage_with_session(self):
        """Helper: return a Storage object with a mocked __session"""
        store = engine.Storage.__new__(engine.Storage)
        store._Storage__session = MagicMock()
        return store

    def test_add_calls_session_add(self):
        """Ensure add() delegates to session.add"""
        store = self.make_storage_with_session()
        obj = object()
        result = store.add(obj)
        store._Storage__session.add.assert_called_once_with(obj)
        self.assertEqual(result, obj)

    def test_get_calls_session_get(self):
        """Ensure get() delegates to session.get"""
        store = self.make_storage_with_session()
        store.get("Model", 5)
        store._Storage__session.get.assert_called_once_with("Model", 5)

    def test_get_by_attr_calls_query_filter_first(self):
        """Ensure get_by_attr() builds a query and calls filter_by"""
        store = self.make_storage_with_session()
        store.get_by_attr("Cls", name="Bread")
        store._Storage__session.query.assert_called_once_with("Cls")
        store._Storage__session.query().filter_by.assert_called_once_with(name="Bread")

    def test_all_with_model_calls_query_all(self):
        """Ensure all(model) returns query results for given model"""
        store = self.make_storage_with_session()
        store.all("Model")
        store._Storage__session.query.assert_called_once_with("Model")
        store._Storage__session.query().all.assert_called_once()

    @patch("models.engine.Base")
    def test_all_without_model_uses_registry_mappers(self, mock_base):
        """Ensure all() with no model iterates Base.registry.mappers"""
        store = self.make_storage_with_session()
        dummy_mapper = MagicMock()
        mock_base.registry.mappers = [dummy_mapper]
        store.all()
        store._Storage__session.query.assert_called_once_with(dummy_mapper)

    def test_all_by_attr_calls_filter_by(self):
        """Ensure all_by_attr() queries and calls filter_by with kwargs"""
        store = self.make_storage_with_session()
        store.all_by_attr("Cls", brand="Peak")
        store._Storage__session.query().filter_by.assert_called_once_with(brand="Peak")

    def test_save_commits(self):
        """Ensure save() calls session.commit"""
        store = self.make_storage_with_session()
        store.save()
        store._Storage__session.commit.assert_called_once()

    def test_delete_removes_object(self):
        """Ensure delete(obj) calls session.delete"""
        store = self.make_storage_with_session()
        obj = object()
        store.delete(obj)
        store._Storage__session.delete.assert_called_once_with(obj)

    def test_delete_with_none_does_nothing(self):
        """Ensure delete(None) does not call session.delete"""
        store = self.make_storage_with_session()
        store.delete(None)
        store._Storage__session.delete.assert_not_called()

    def test_rollback_calls_session(self):
        """Ensure rollback() calls session.rollback"""
        store = self.make_storage_with_session()
        store.rollback()
        store._Storage__session.rollback.assert_called_once()

    def test_close_calls_remove(self):
        """Ensure close() calls session.remove"""
        store = self.make_storage_with_session()
        store.close()
        store._Storage__session.remove.assert_called_once()

    @patch("models.engine.scoped_session")
    @patch("models.engine.sessionmaker")
    @patch("models.engine.Base.metadata.create_all")
    def test_reload_sets_session(self, mock_create, mock_smaker, mock_scoped):
        """Ensure reload() creates metadata and sets a scoped_session"""
        store = engine.Storage.__new__(engine.Storage)
        store._Storage__engine = MagicMock()
        mock_scoped.return_value = "ScopedSession"
        store.reload()
        mock_create.assert_called_once_with(store._Storage__engine)
        self.assertEqual(store._Storage__session, "ScopedSession")


if __name__ == "__main__":
    unittest.main()

