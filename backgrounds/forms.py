from django import forms

class GridForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Grid Name")
    rows = forms.IntegerField(min_value=1, required=True, label="Number of Rows")
    cols = forms.IntegerField(min_value=1, required=True, label="Number of Columns")

class DotForm(forms.Form):
    row = forms.IntegerField(min_value=0, required=True, label="Row Coordinate")
    col = forms.IntegerField(min_value=0, required=True, label="Col Coordinate")
    color = forms.CharField(max_length=7, required=True, label="Dot Color (Hex Code)")