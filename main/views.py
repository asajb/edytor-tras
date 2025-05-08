from django.shortcuts import render
from backgrounds.models import BackgroundImage
from routes.models import Route
# Create your views here.

def home_view(request):
    bgid = request.GET.get('bg')
    background = (BackgroundImage.objects.filter(id=bgid).first() 
                  if bgid else BackgroundImage.objects.first())
    backgrounds = BackgroundImage.objects.all()
    user_routes = Route.objects.filter(user=request.user, background=background) if request.user.is_authenticated else []
    return render(request, 'main/home.html', {
        'background': background,
        'backgrounds': backgrounds,
        'user_routes': user_routes,
    })