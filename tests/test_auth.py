#!/usr/bin/env python3
import unittest
import requests

BASE_URL = "http://localhost:5000"


class TestAuthFlow(unittest.TestCase):
    email = "testuser@example.com"
    password = "secret123"
    access_token = None

    user_payload = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "email": email,
        "password": password,
        "whatsapp_number": "1234567890",
        "other_name": "T",
        "address": "123 Test Street",
        "phone_number": "08011112222",
        "city": "TestCity",
        "state": "TestState",
        "country": "TestCountry",
    }

    def test_0_register_missing_fields(self):
        """Should fail if required fields are missing"""
        bad_payload = {"email": self.email}
        r = requests.post(f"{BASE_URL}/register", json=bad_payload)
        self.assertEqual(r.status_code, 400)
        print("Register missing fields:", r.json())

    def test_1_register(self):
        """Register a new user with all required fields"""
        r = requests.post(f"{BASE_URL}/register", json=self.user_payload)
        self.assertIn(r.status_code, (201, 400))  
        print("Register response:", r.json())

    def test_2_login(self):
        """Login and get tokens"""
        r = requests.post(f"{BASE_URL}/login", json={
            "email": self.email,
            "password": self.password
        })
        self.assertEqual(r.status_code, 200, msg=r.text)
        data = r.json()
        self.__class__.access_token = data["access_token"]
        print("Login response:", data)

    def test_3_protected_no_token(self):
        """Fail to access protected route without token"""
        r = requests.get(f"{BASE_URL}/orders")
        self.assertEqual(r.status_code, 401)  # Unauthorized
        print("Protected (no token):", r.json())

    def test_4_protected_with_token(self):
        """Succeed with token"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        r = requests.get(f"{BASE_URL}/orders", headers=headers)
        self.assertEqual(r.status_code, 200, msg=r.text)
        print("Protected (with token):", r.json())


if __name__ == "__main__":
    unittest.main()
