#!/usr/bin/env python3

import sqlite3
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker

# Define a base
Base = declarative_base()

# Define a simple User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)


# Setup SQLite in-memory DB
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Insert first user
u1 = User(id=1, email="test@example.com")
session.add(u1)
session.commit()

# Try inserting a duplicate (same email) -> should raise IntegrityError
u2 = User(id=2, email="test@example.com")
session.add(u2)

try:
    session.commit()
except IntegrityError as e:
    print("Caught IntegrityError!")
    print(help(e))
    print(e.orig)
    session.rollback()
