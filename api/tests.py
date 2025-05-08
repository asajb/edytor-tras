from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from backgrounds.models import BackgroundImage
from routes.models import Route, RoutePoint

class ApiRoutesTest(APITestCase):
    def setUp(self):
        # Create a test user and a background image.
        self.user = User.objects.create_user(username='apitestuser', password='apipass')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.bg = BackgroundImage.objects.create(name='Test Background', image='backgrounds/test.jpg')
        # Authenticate as the test user using force_authenticate.
        self.client.force_authenticate(user=self.user)
    
    def test_create_route(self):
        url = reverse('trasa-list')
        data = {
            "name": "API Route",
            "background": self.bg.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        route_id = response.data['id']
        route = Route.objects.get(id=route_id)
        self.assertEqual(route.user, self.user)
        self.assertEqual(route.name, "API Route")
    
    def test_get_routes_only_user_routes(self):
        # Create a route owned by the authenticated user...
        Route.objects.create(user=self.user, background=self.bg, name="User Route")
        # ...and one owned by another user.
        Route.objects.create(user=self.other_user, background=self.bg, name="Other Route")
        url = reverse('trasa-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only one route (the one owned by self.user) should be returned.
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "User Route")
    
    def test_get_route_detail(self):
        route = Route.objects.create(user=self.user, background=self.bg, name="Detail Route")
        url = reverse('trasa-detail', args=[route.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Detail Route")
    
    def test_delete_route(self):
        route = Route.objects.create(user=self.user, background=self.bg, name="Delete Route")
        url = reverse('trasa-detail', args=[route.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Route.objects.filter(id=route.id).exists())
    
    def test_create_route_point(self):
        route = Route.objects.create(user=self.user, background=self.bg, name="Point Route")
        url = reverse('punkt-list', kwargs={'trasa_id': route.id})
        data = {
            "x": 100.0,
            "y": 200.0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # The perform_create for points calculates the order automatically (starting at 0+1)
        point = RoutePoint.objects.get(route=route)
        self.assertEqual(point.order, 1)
        self.assertEqual(point.x, 100.0)
        self.assertEqual(point.y, 200.0)
    
    def test_get_route_points(self):
        route = Route.objects.create(user=self.user, background=self.bg, name="Points Route")
        RoutePoint.objects.create(route=route, x=10.0, y=20.0, order=1)
        RoutePoint.objects.create(route=route, x=15.0, y=25.0, order=2)
        url = reverse('punkt-list', kwargs={'trasa_id': route.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_delete_route_point(self):
        route = Route.objects.create(user=self.user, background=self.bg, name="Delete Point Route")
        point = RoutePoint.objects.create(route=route, x=10.0, y=20.0, order=1)
        url = reverse('punkt-detail', kwargs={'trasa_id': route.id, 'pk': point.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RoutePoint.objects.filter(id=point.id).exists())
    
    def test_api_authentication_enforced(self):
        # Ensure that requests without proper authentication are denied.
        self.client.force_authenticate(user=None)
        url = reverse('trasa-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])