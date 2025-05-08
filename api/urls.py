from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .routes_api import RouteViewSet, RoutePointViewSet

router = DefaultRouter()
router.register(r'trasy', RouteViewSet, basename='trasa')

urlpatterns = [
    path('', include(router.urls)),
    path('trasy/<int:trasa_id>/punkty/', RoutePointViewSet.as_view({
         'get': 'list',
         'post': 'create'
    }), name='punkt-list'),
    # GET i DELETE: /api/trasy/<trasa_id>/punkty/<punkt_id>/
    path('trasy/<int:trasa_id>/punkty/<int:pk>/', RoutePointViewSet.as_view({
         'get': 'retrieve',
         'delete': 'destroy'
    }), name='punkt-detail'),
]