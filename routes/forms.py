from django import forms
from .models import RoutePoint

class RouteForm(forms.Form):
    route_name = forms.CharField(max_length=100, required=True, label="Route Name")

class RoutePointForm(forms.Form):
    x = forms.FloatField(required=True, label="X Coordinate")
    y = forms.FloatField(required=True, label="Y Coordinate")

class RoutePointModelForm(forms.ModelForm):
    class Meta:
        model = RoutePoint
        fields = ['id', 'x', 'y']