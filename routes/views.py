from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory, modelformset_factory
from django.contrib.auth.decorators import login_required
from django.db import models
from backgrounds.models import BackgroundImage
from .models import Route, RoutePoint
from .forms import RouteForm, RoutePointForm, RoutePointModelForm

@login_required
def create_route(request):
    bgid = request.GET.get('bg')
    background = (BackgroundImage.objects.filter(id=bgid).first() 
                  if bgid else BackgroundImage.objects.first())
    RoutePointFormSet = formset_factory(RoutePointForm, extra=1)
    if request.method == "POST":
        route_form = RouteForm(request.POST)
        formset = RoutePointFormSet(request.POST)
        if route_form.is_valid() and formset.is_valid():
            # Create the route for the current user and background
            route_name = route_form.cleaned_data['route_name']
            route = Route.objects.create(user=request.user, background=background, name=route_name)
            order = 1
            # Create associated route points only for forms with values
            for point_form in formset:
                x = point_form.cleaned_data.get('x')
                y = point_form.cleaned_data.get('y')
                if x is not None and y is not None:
                    RoutePoint.objects.create(route=route, x=x, y=y, order=order)
                    order += 1
            return redirect('')  # Redirect to homepage (as defined in main/urls.py)
    else:
        route_form = RouteForm()
        formset = RoutePointFormSet()
    return render(request, 'routes/create_route.html', {
        'background': background,
        'route_form': route_form,
        'formset': formset
    })

@login_required
def route_detail(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    points = route.points.all()
    return render(request, 'routes/route.html', {
        'route': route,
        'points': points,
    })

@login_required
def edit_route(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    RoutePointFormSet = modelformset_factory(RoutePoint, form=RoutePointModelForm, can_delete=True, extra=1)
    if request.method == "POST":
        formset = RoutePointFormSet(request.POST, queryset=route.points.all())
        if formset.is_valid():
            instances = formset.save(commit=False)

            # Delete marked objects first
            for obj in formset.deleted_objects:
                obj.delete()
            
            
            
            # Get the maximum order of existing points
            max_order = route.points.aggregate(models.Max('order'))['order__max'] or 0
            
            for instance in instances:
                if instance.pk is None:  # This is a new point
                    instance.order = max_order + 1
                    max_order += 1
                instance.route = route
                instance.save()
            
            return redirect('route_detail', route_id=route.id)
        else:
            print("Formset errors:", formset.errors)
    else:
        formset = RoutePointFormSet(queryset=route.points.all())
    return render(request, 'routes/edit_route.html', {
        'route': route,
        'formset': formset
    })