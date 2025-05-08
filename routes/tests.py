from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from backgrounds.models import BackgroundImage
from .models import Route, RoutePoint
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

class RouteModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_image = SimpleUploadedFile(
            name='test.jpg',
            content=b'\x47\x49\x46\x38\x39\x61',  # minimal GIF header bytes
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.background = BackgroundImage.objects.create(
            name="Test Background",
            image=cls.test_image
        )
        cls.route = Route.objects.create(user=cls.user, background=cls.background, name="Test Route")

    def test_route_str(self):
        self.assertEqual(str(self.route), "Test Route")

    def test_route_relation(self):
        # Sprawdzamy, czy trasa jest powiązana z użytkownikiem i tłem
        self.assertEqual(self.route.user, self.user)
        self.assertEqual(self.route.background, self.background)

    def test_route_update(self):
        # Test updating and saving the Route instance
        self.route.name = "Updated Route"
        self.route.save()
        updated_route = Route.objects.get(pk=self.route.pk)
        self.assertEqual(updated_route.name, "Updated Route")

class RoutePointModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.background = BackgroundImage.objects.create(name="Test Background", image="backgrounds/test.jpg")
        cls.route = Route.objects.create(user=cls.user, background=cls.background, name="Test Route")
        cls.point1 = RoutePoint.objects.create(route=cls.route, x=10.0, y=20.0, order=1)
        cls.point2 = RoutePoint.objects.create(route=cls.route, x=15.0, y=25.0, order=2)
        cls.point3 = RoutePoint.objects.create(route=cls.route, x=20.0, y=30.0, order=3)

    def test_route_point_str(self):
        expected1 = "Point 1 (10.0, 20.0)"
        expected2 = "Point 2 (15.0, 25.0)"
        expected3 = "Point 3 (20.0, 30.0)"
        self.assertEqual(str(self.point1), expected1)
        self.assertEqual(str(self.point2), expected2)
        self.assertEqual(str(self.point3), expected3)

    def test_route_point_ordering(self):
        # Sprawdzamy, czy punkty są posortowane według kolejności
        points = list(self.route.points.all())
        self.assertEqual(points[0], self.point1)
        self.assertEqual(points[1], self.point2)
        self.assertEqual(points[2], self.point3)

    def test_route_point_relation(self):
        # Sprawdzamy, czy punkty są powiązane z trasą
        self.assertEqual(self.point1.route, self.route)
        self.assertEqual(self.point2.route, self.route)
        self.assertEqual(self.point3.route, self.route) 

    def test_route_point_deletion(self):
        # Sprawdzamy, czy usunięcie trasy usuwa również punkty
        route_id = self.route.id
        self.route.delete()
        with self.assertRaises(RoutePoint.DoesNotExist):
            RoutePoint.objects.get(route_id=route_id)

class RouteAuthorizationTest(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass2")
        # Create a background image instance for routes
        self.bg = BackgroundImage.objects.create(name="Test Background", image="backgrounds/test.jpg")
        # Create one route for each user
        self.route1 = Route.objects.create(user=self.user1, background=self.bg, name="User1 Route")
        self.route2 = Route.objects.create(user=self.user2, background=self.bg, name="User2 Route")

    def test_redirect_for_anonymous(self):
        # Attempt to access a protected route without login
        url = reverse('route_detail', args=[self.route1.id])
        response = self.client.get(url)
        # By default, Django's login_required redirects to /accounts/login/?next=<url> or your custom login url
        self.assertNotEqual(response.status_code, 200)
        self.assertIn("login", response.url)

    def test_logged_in_user_access_own_route(self):
        # Log in as user1 and access their own route
        self.client.login(username="user1", password="pass1")
        url = reverse('route_detail', args=[self.route1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Optionally check that the route name is on the page
        self.assertContains(response, "User1 Route")

    def test_logged_in_user_cannot_access_other_users_route(self):
        # Log in as user1 and try to access user2's route
        self.client.login(username="user1", password="pass1")
        url = reverse('route_detail', args=[self.route2.id])
        response = self.client.get(url)
        # The view uses get_object_or_404 filtering by user, so non-owner returns 404
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        # Log in then log out, ensure that accessing a protected page afterward redirects to login.
        self.client.login(username="user1", password="pass1")
        self.client.logout()
        url = reverse('route_detail', args=[self.route1.id])
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertIn("login", response.url)


    
    
    