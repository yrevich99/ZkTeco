from django import forms
from django.forms import fields
from .models import Department

class AddDeviceForm(forms.Form):
    device_name = forms.CharField()
    device_ip = forms.CharField()
    device_port = forms.CharField()
    # main_door = forms.CharField()

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('name', 'parent')