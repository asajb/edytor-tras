from django.contrib import admin
from .models import BackgroundImage, GameBoard, UserPath, PathsOnBoard

# Register your models here.

admin.site.register(BackgroundImage)
admin.site.register(GameBoard)
admin.site.register(UserPath)
admin.site.register(PathsOnBoard)