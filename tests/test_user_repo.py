#!/usr/bin/env python3
"""
Test script for the UserRepo class.
Run this directly to validate UserRepo functionality.
"""

from repositories.user_repo import UserRepo
from models import storage


def run_tests():
    print("=== UserRepo Tests ===")

    # 1. Create a new user
    print("\n[1] Creating a new user...")
    user = UserRepo.new(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email="johndoe@example.com",
        password="supersecret",
        whatsapp_number="2348012345678",
        phone_number="2348098765432",
        address="123 Market Street",
        city="Lagos",
        state="Lagos",
        country="Nigeria",
        is_admin=False,
    )
    print("Created:", user)

    # 2. Retrieve by ID
    print("\n[2] Retrieve by ID...")
    fetched = UserRepo.get(user.id)
    print("Fetched:", fetched)

    # 3. Retrieve by username
    print("\n[3] Retrieve by username...")
    u_by_username = UserRepo.get_by_username("johndoe")
    print("By username:", u_by_username)

    # 4. Retrieve by email
    print("\n[4] Retrieve by email...")
    u_by_email = UserRepo.get_by_email("johndoe@example.com")
    print("By email:", u_by_email)

    # 5. Retrieve by WhatsApp
    print("\n[5] Retrieve by WhatsApp...")
    u_by_whatsapp = UserRepo.get_by_whatsapp("2348012345678")
    print("By WhatsApp:", u_by_whatsapp)

    # 6. Password check
    print("\n[6] Password check...")
    print("Correct password:", user.check_password("supersecret"))
    print("Wrong password:", user.check_password("wrongpass"))

    # 7. Update user
    print("\n[7] Updating user (city -> Abuja, is_admin -> True)...")
    updated = UserRepo.update(id=user.id, city="Abuja", is_admin=True)
    print("Updated:", updated)

    # 8. Retrieve all users
    print("\n[8] Retrieve all users...")
    all_users = UserRepo.all()
    print("All users:", all_users)

    # 9. Delete user
    print("\n[9] Deleting user...")
    deleted = UserRepo.delete(user.id)
    print("Deleted:", deleted)

    # 10. Confirm deletion
    print("\n[10] Confirm deletion...")
    check_deleted = UserRepo.get(user.id)
    print("Still exists?:", check_deleted)


if __name__ == "__main__":
    run_tests()
    storage.close()
