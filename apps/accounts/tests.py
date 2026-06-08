from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class SignupViewTests(TestCase):
    def test_signup_creates_account(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "full_name": "Alice Landlord",
                "email": "alice@example.com",
                "phone": "1234567890",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )
        self.assertRedirects(response, reverse("dashboard:home"))
        self.assertTrue(User.objects.filter(email="alice@example.com").exists())

    def test_signup_rejects_weak_password(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "full_name": "Alice Landlord",
                "email": "alice@example.com",
                "phone": "1234567890",
                "password1": "password",
                "password2": "password",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="alice@example.com").exists())

    def test_profile_rejects_duplicate_email(self):
        user = User.objects.create_user(email="owner@example.com", password="StrongPass123", full_name="Owner")
        User.objects.create_user(email="other@example.com", password="StrongPass123", full_name="Other")
        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts:profile"),
            {
                "full_name": "Owner",
                "email": "other@example.com",
                "phone": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.email, "owner@example.com")
