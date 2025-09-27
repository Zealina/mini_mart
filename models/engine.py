#!/usr/bin/env python3
"""Storage engine"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from dotenv_vault import load_dotenv
from os import getenv


load_dotenv()


class Storage:
    """SQLAlchemy storage engine"""

    __engine = None
    __session = None

    def __init__(self):
        """Instantiate a Storage object"""
        USER = getenv('MINI_MART_MYSQL_USER')
        PWD = getenv('MINI_MART_MYSQL_PWD')
        HOST = getenv('MINI_MART_MYSQL_HOST')
        DB = getenv('MINI_MART_MYSQL_DB')
        ENV = getenv('MINI_MART_ENV')
        if USER and PWD and HOST and DB and ENV:
            url = f"mysql+pymysql://{USER}:{PWD}@{HOST}/{DB}"
        else:
            raise ValueError("Set all DB env variables")
        self.__engine = create_engine(url)
#        if ENV == "test":
#            Base.metadata.drop_all(self.__engine)

    def add(self, obj):
        """Add an object to the session"""
        self.__session.add(obj)
        return obj

    def get(self, model, obj_id):
        """Fetch one object by id"""
        obj = self.__session.get(model, obj_id)
        return obj

    def get_by_attr(self, cls, **kwargs):
        """Get one object by attribute(s)"""
        return self.__session.query(cls).filter_by(**kwargs).first()

    def all(self, model=None, base=None):
        """Fetch all objects of a model"""
        session = self.__session
        if not model:
            result = []
            models = Base.registry.mappers
            if base:
                models = base.registry.mappers
            for model in models:
                result.append(session.query(model).all())
            return result
        objs = session.query(model).all()
        return objs

    def all_by_attr(self, cls, **kwargs):
        """Get all objects by attribute(s)"""
        return self.__session.query(cls).filter_by(**kwargs)

    def save(self):
        """commit all changes of the current database session"""
        self.__session.commit()

    def delete(self, obj=None):
        """delete from the current database session obj if not None"""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """reloads data from the database"""
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session

    def close(self):
        """call remove() method on the session attribute"""
        self.__session.remove()

    def rollback(self):
        """rollback changes to db"""
        self.__session.rollback()
