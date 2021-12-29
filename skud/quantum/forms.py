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

class CreateAccess(forms.Form):
    access_name = forms.CharField(max_length=150)
    lock_control = forms.CharField(max_length = 150)
    time_zone = forms.CharField(max_length = 150)
    
    
    