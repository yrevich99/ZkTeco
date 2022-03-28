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
    
class CreateUser(forms.Form):
    userId = forms.CharField(max_length=150)
    images = forms.CharField(max_length=150)
    surname = forms.CharField(max_length=150)
    name = forms.CharField(max_length=150)
    department = forms.CharField(max_length=150)
    card_number = forms.CharField(max_length=50)
    access_id = forms.CharField(max_length=150)

class CreateSmena(forms.Form):
    smena_name = forms.CharField(max_length=60)
    start_time = forms.TimeField()
    end_time = forms.TimeField()
    start_break = forms.TimeField()
    end_break = forms.TimeField()
    