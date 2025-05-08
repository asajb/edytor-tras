from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from backgrounds.models import BackgroundImage
from .models import Route, RoutePoint

class RouteManagementTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user and a background image.
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.bg = BackgroundImage.objects.create(
            name="Test Background", image="backgrounds/test.jpg"
        )
    
    def setUp(self):
        # Log in the user for each test.
        self.client.login(username="testuser", password="testpass")

    def test_display_list_of_user_routes(self):
        # Create some routes for the user
        Route.objects.create(user=self.user, background=self.bg, name="User Route 1")
        Route.objects.create(user=self.user, background=self.bg, name="User Route 2")
        url = reverse('')  # Home view should show
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Route 1")
        self.assertContains(response, "User Route 2")

    def test_create_empty_route_with_background(self):
        # Create a route without any points.
        url = reverse('create_route') + f"?bg={self.bg.id}"
        data = {
            "route_name": "Empty Route",
            # Management form for the RoutePointFormSet (formset factory using RoutePointForm expects these fields)
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-x": "",  # no coordinate value
            "form-0-y": "",
        }
        response = self.client.post(url, data)
        # Expect a redirect after creation
        self.assertEqual(response.status_code, 302)
        route = Route.objects.get(name="Empty Route", user=self.user)
        # Since no points were provided, expect 0 points
        self.assertEqual(route.points.count(), 0)

    def test_create_route_with_points(self):
        # Create a route and add one point through the form.
        url = reverse('create_route') + f"?bg={self.bg.id}"
        data = {
            "route_name": "Route With Point",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-x": "12.5",
            "form-0-y": "22.5",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        route = Route.objects.get(name="Route With Point", user=self.user)
        self.assertEqual(route.points.count(), 1)
        point = route.points.first()
        self.assertEqual(point.x, 12.5)
        self.assertEqual(point.y, 22.5)

    def test_edit_route_remove_point(self):
        # Create a route with a point, then simulate editing to remove point.
        route = Route.objects.create(user=self.user, background=self.bg, name="Route To Edit")
        point = RoutePoint.objects.create(route=route, x=10.0, y=20.0, order=1)
        url = reverse('edit_route', args=[route.id])
        # Prepare form data for the modelformset used in edit_route view.
        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "1",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            # Include the primary key so the form recognizes an existing point.
            "form-0-id": str(point.id),
            "form-0-x": "10.0",
            "form-0-y": "20.0",
            # Mark for deletion
            "form-0-DELETE": "on",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        # After deletion, points for the route should be 0.
        self.assertEqual(route.points.count(), 0)