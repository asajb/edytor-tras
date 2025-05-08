from django.urls import path
from . import views

urlpatterns = [
    path('create_route/', views.create_route, name='create_route'),
    path('route/<int:route_id>/', views.route_detail, name='route_detail'),
    path('route/<int:route_id>/edit/', views.edit_route, name='edit_route'),
]