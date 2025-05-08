from rest_framework import viewsets, permissions
from routes.models import Route, RoutePoint
from routes.serializers import RouteSerializer, RoutePointSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Max

class RouteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows routes to be viewed, created, and deleted.
    """
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow a user to see their own routes
        return Route.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Save the route with the current user
        serializer.save(user=self.request.user)

class RoutePointViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows route points to be viewed, created, and deleted.
    """
    serializer_class = RoutePointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow a user to see their own route points
        route_id = self.kwargs.get('trasa_id')
        return RoutePoint.objects.filter(route__id=route_id, route__user=self.request.user)
    
    def perform_create(self, serializer):
        # Save the route point with the current user
        route_id = self.kwargs.get('trasa_id')
        route = get_object_or_404(Route, id=route_id, user=self.request.user)
        max_order = route.points.aggregate(Max('order'))['order__max'] or 0
        serializer.save(route=route, order=max_order + 1)