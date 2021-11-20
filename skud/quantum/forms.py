from django import forms

class AddDeviceForm(forms.Form):
    device_name = forms.CharField()
    device_ip = forms.CharField()
    device_port = forms.CharField()
    # main_door = forms.CharField()