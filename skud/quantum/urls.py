from django.urls import path
from . import views

app_name = 'quantum'

urlpatterns = [
    path('',views.user_list, name='user_list'),
    path('search_device', views.search_device, name='search_device'),
    path('device_list', views.device_list, name='device_list'),
    path('add_device',views.add_device, name='add_device'),
    path('delete_device/<str:device_ip>',views.delete_device),
]