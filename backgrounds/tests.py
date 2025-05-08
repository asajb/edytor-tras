from django.test import TestCase
from .models import BackgroundImage
from django.urls import reverse
from django.contrib.auth.models import User
# Create your tests here.

class BackgroundImageTest(TestCase):
    def setUp(self):
        self.bg = BackgroundImage.objects.create(
            name="Test Background",
            image="backgrounds/test.jpg"
        )

    def test_background_str(self):
        self.assertEqual(str(self.bg), "Test Background")

    def test_background_instance(self):
        self.assertIsInstance(self.bg, BackgroundImage)
        self.assertEqual(self.bg.name, "Test Background")
        self.assertEqual(self.bg.image, "backgrounds/test.jpg")

class LoginRequiredTest(TestCase):
    def test_redirect_for_anonymous(self):
        # Try to access the dashboard without logging in.
        response = self.client.get(reverse('dashboard'))
        # Check for redirect (status 302) to login
        self.assertEqual(response.status_code, 302)
        # The login URL should appear in the redirection URL.
        self.assertIn(reverse('login'), response.url)

    def test_access_for_authenticated_user(self):
        # Create and login a test user.
        user = User.objects.create_user(username="testuser", password="securepass")
        self.client.login(username="testuser", password="securepass")
        # Now access the dashboard.
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        # Optionally, verify that the dashboard page contains expected content:
        self.assertContains(response, "dashboard")