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
        """Create and store a new user."""
        kwargs.pop("is_admin", None)
        kwargs.pop("is_super_admin", None)

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
            is_admin=False,
            is_super_admin=False,
            bank_name=kwargs.get("bank_name"),
            account_number=kwargs.get("account_number"),
            account_name=kwargs.get("account_name"),
        )
        user.password = kwargs["password"]

        try:
            user.save()
        except IntegrityError:
            storage.rollback()
            raise

        return user

    @classmethod
    def get(cls, user_id: str) -> User | None:
        """Retrieve a user by ID."""
        return storage.get(User, user_id)

    @classmethod
    def all(cls) -> list[User]:
        """Retrieve all users."""
        return storage.all(User)

    @classmethod
    def update(cls, user_id=None, **kwargs) -> User | None:
        """Update a user while preserving legacy behavior and super-admin mirroring."""
        if user_id is None:
            user_id = kwargs.pop("id", None)

        if not user_id:
            return None

        user = cls.get(user_id)
        if not user:
            return None

        allowed_keys = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "whatsapp_number",
            "address",
            "password",
            "is_admin",
            "is_super_admin",
            "bank_name",
            "account_number",
            "account_name",
        ]


        for key, value in kwargs.items():
            if key not in allowed_keys:
                continue
            if key == "password":
                user.password = value
            else:
                setattr(user, key, value)

        bank_keys = ["bank_name", "account_number", "account_name"]
        is_super = getattr(user, "is_super_admin", False)
        if is_super in [True, 1, "1", "true", "True"] and any(
            key in kwargs for key in bank_keys
        ):
            for other_user in storage.all(User):
                other_is_super = getattr(other_user, "is_super_admin", False)
                if other_is_super in [True, 1, "1", "true", "True"] and other_user.id != user.id:
                    other_user.bank_name = getattr(user, "bank_name", "")
                    other_user.account_number = getattr(user, "account_number", "")
                    other_user.account_name = getattr(user, "account_name", "")
        storage.save()
        return user

    @classmethod
    def delete(cls, user_id: str) -> bool:
        """Delete a user by ID."""
        user = cls.get(user_id)
        if not user:
            return False
        storage.delete(user)
        storage.save()
        return True

    @classmethod
    def get_by_username(cls, username: str) -> User | None:
        """Retrieve a user by username."""
        return storage.get_by_attr(User, username=username)

    @classmethod
    def get_by_email(cls, email: str) -> User | None:
        """Retrieve a user by email."""
        return storage.get_by_attr(User, email=email)

    @classmethod
    def get_by_whatsapp(cls, whatsapp_number: str) -> User | None:
        """Retrieve a user by WhatsApp number."""
        return storage.get_by_attr(User, whatsapp_number=whatsapp_number)
