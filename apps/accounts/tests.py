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
