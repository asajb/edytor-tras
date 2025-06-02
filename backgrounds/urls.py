from django.urls import path
from . import views

urlpatterns = [
    path('create_grid/', views.create_grid, name='create_grid'),
    path('edit_grid/<int:grid_id>/', views.edit_grid, name='edit_grid'),
    path('list_grids/', views.list_grids, name='list_grids'),
    path('make_paths_on_grid/<int:grid_id>/', views.make_paths_on_grid, name='make_paths_on_grid'),
    path('show_paths_on_grid/<int:grid_id>/<int:path_id>/', views.show_paths_on_grid, name='show_paths_on_grid'),
    path('sse/notifications/', views.sse_notifications, name='sse_notifications'),
]