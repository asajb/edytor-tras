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

