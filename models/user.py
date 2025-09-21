#!/usr/bin/env python3
"""User Model"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from models.base_model import Base, BaseModel


class User(Base, BaseModel):
    """
    Represents a user in the Mini Mart system.

    Attributes:
        first_name (str): User's first name.
        last_name (str): User's last name.
        other_name (str): Optional other name or middle name.
        username (str): Unique username, used for login.
        email (str): Unique email address of the user.
        phone_number (str): Optional unique phone number.
        whatsapp_number (str): Required unique WhatsApp number.
        address (str): Optional address of the user.
        city (str): Optional city where the user resides.
        state (str): Optional state where the user resides.
        country (str): Optional country where the user resides.
        __password (str): Hashed password stored internally.
        is_admin (bool): Flag to determine if the user is an admin.
        orders (relationship): Relationship to the user's orders.
    """

    __tablename__ = "users"

    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    other_name = Column(String(128), nullable=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=False, index=True)
    phone_number = Column(String(32), unique=True, nullable=True, index=True)
    whatsapp_number = Column(String(32), unique=True, nullable=False, index=True)
    address = Column(String(256), nullable=True)
    city = Column(String(64), nullable=True)
    state = Column(String(64), nullable=True)
    country = Column(String(64), nullable=True)
    __password = Column("password", String(256), nullable=False)
    is_admin = Column(Boolean, default=False)

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


    def __repr__(self):
        """
        Returns a string representation of the User instance.
        """
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


    @property
    def password(self):
        """
        Prevent direct access to the password attribute.
        Raises:
            AttributeError: Always, because password should be write-only.
        """
        raise AttributeError("Password is write-only.")


    @password.setter
    def password(self, plaintext_password):
        """
        Hashes and sets the user's password.
        
        Args:
            plaintext_password (str): The raw password to be hashed.
        """
        self.__password = generate_password_hash(plaintext_password)


    def check_password(self, plaintext_password):
        """
        Verifies if a given password matches the stored hashed password.
        
        Args:
            plaintext_password (str): The password to verify.
        
        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.__password, plaintext_password)
