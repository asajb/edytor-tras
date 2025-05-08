from django.db import models
from django.contrib.auth.models import User
from backgrounds.models import BackgroundImage

# Create your models here.

class Route(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    background = models.ForeignKey(BackgroundImage, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name or f"Route {self.pk} by {self.user.username}"
    
class RoutePoint(models.Model):
    route = models.ForeignKey(Route, related_name='points', on_delete=models.CASCADE)
    x = models.FloatField()
    y = models.FloatField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Point {self.order} ({self.x}, {self.y})"