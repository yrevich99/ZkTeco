from django.urls import path
from . import views

app_name = 'quantum'

urlpatterns = [
    path('',views.user_list, name='user_list'),
    path('search_devices_list', views.search_device_list, name='search_device'),
    path('device_list', views.device_list, name='device_list'),
    path('add_device',views.add_device, name='add_device'),
    path('edit_device/<int:id>', views.edit_device, name='edit_device'),
    path('delete_device/<str:device_ip>',views.delete_device),
    path('device_list/<int:id>', views.current_time, name='current_time'),
    path('access_control',views.access_control),
    path('door_settings', views.door_setting_list),
    
]