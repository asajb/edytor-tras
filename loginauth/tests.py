from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username="testuser", password="securepass")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("securepass"))