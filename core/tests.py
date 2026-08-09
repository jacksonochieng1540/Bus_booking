from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="password123",
            first_name="Jane",
            last_name="Doe",
        )

    def test_register_view_success(self):
        url = reverse("core:register")
        payload = {
            "username": "newuser",
            "first_name": "John",
            "last_name": "Smith",
            "email": "newuser@example.com",
            "password": "securepassword",
            "confirm_password": "securepassword",
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_password_mismatch(self):
        url = reverse("core:register")
        payload = {
            "username": "mismatchuser",
            "first_name": "John",
            "last_name": "Smith",
            "email": "mismatch@example.com",
            "password": "securepassword",
            "confirm_password": "wrongpassword",
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="mismatchuser").exists())

    def test_login_view_success(self):
        url = reverse("core:login")
        payload = {
            "username": "existinguser",
            "password": "password123",
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, 302)

    def test_api_register_success(self):
        url = reverse("core:api_register")
        payload = {
            "username": "apipassenger",
            "first_name": "API",
            "last_name": "User",
            "email": "api@example.com",
            "password": "apipassword123",
            "confirm_password": "apipassword123",
        }
        response = self.client.post(url, data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["user"]["username"], "apipassenger")

    def test_api_login_success(self):
        url = reverse("core:api_login")
        payload = {
            "username": "existinguser",
            "password": "password123",
        }
        response = self.client.post(url, data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user"]["username"], "existinguser")
