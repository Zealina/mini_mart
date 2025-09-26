#!/usr/bin/env python3
"""
Repository class for managing User operations.
Provides methods to create, retrieve, update, and delete User objects.
"""

from models import storage
from models.user import User
from sqlalchemy.exc import IntegrityError


class UserRepo:
    """Repository class to manage user operations"""

    @classmethod
    def new(cls, **kwargs) -> User:
        """Create and store a new user"""
        required_fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "whatsapp_number",
        ]
        for field in required_fields:
            if not kwargs.get(field):
                raise ValueError(f"Missing {field}")

        user = User(
            first_name=kwargs["first_name"],
            last_name=kwargs["last_name"],
            email=kwargs["email"],
            phone_number=kwargs.get("phone_number"),
            whatsapp_number=kwargs["whatsapp_number"],
            address=kwargs.get("address"),
            is_admin=kwargs.get("is_admin", False),
        )
        user.password = kwargs["password"]

        try:
            user.save()
        except IntegrityError as e:
            detail = str(e.orig).lower() if e.orig else str(e).lower()

            for entry in required_fields:
                if entry in detail:
                    raise ValueError(f"{entry} already exists!")
            raise ValueError("A unique field already exists!")

        return user


    @classmethod
    def get(cls, user_id: str) -> User | None:
        """
        Retrieve a user by ID.

        Args:
            user_id (str): UUID of the user.

        Returns:
            User | None: The user instance if found, else None.
        """
        return storage.get(User, user_id)


    @classmethod
    def all(cls) -> list[User]:
        """
        Retrieve all users.

        Returns:
            list[User]: List of all user instances.
        """
        return storage.all(User)


    @classmethod
    def update(cls, **kwargs) -> User | None:
        """
        Update user details.

        Args:
            kwargs: Must include "id" of the user and the fields to update.

        Returns:
            User | None: Updated user instance, or None if not found/invalid.
        """
        user_id = kwargs.get("id")
        if not user_id:
            return None

        user = cls.get(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if key == "password":
                user.password = value
            elif key != "id" and hasattr(user, key):
                setattr(user, key, value)

        user.save()
        return user


    @classmethod
    def delete(cls, user_id: str) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id (str): UUID of the user.

        Returns:
            bool: True if deleted, False otherwise.
        """
        user = cls.get(user_id)
        if not user:
            return False
        storage.delete(user)
        storage.save()
        return True


    @classmethod
    def get_by_username(cls, username: str) -> User | None:
        """
        Retrieve a user by username.

        Args:
            username (str): The username to search.

        Returns:
            User | None: User if found, else None.
        """
        return storage.get_by_attr(User, username=username)


    @classmethod
    def get_by_email(cls, email: str) -> User | None:
        """
        Retrieve a user by email.

        Args:
            email (str): The email to search.

        Returns:
            User | None: User if found, else None.
        """
        return storage.get_by_attr(User, email=email)


    @classmethod
    def get_by_whatsapp(cls, whatsapp_number: str) -> User | None:
        """
        Retrieve a user by WhatsApp number.

        Args:
            whatsapp_number (str): The WhatsApp number to search.

        Returns:
            User | None: User if found, else None.
        """
        return storage.get_by_attr(User, whatsapp_number=whatsapp_number)
