from django.urls import path
from . import views

app_name = 'quantum'

urlpatterns = [
    path('users_list',views.user_list, name='user_list'),
    path('search_devices_list', views.search_list),
    path('search_devices_list/all', views.search_device_list, name='search_device_list'),
    path('device_list', views.device_list, name='device_list'),
    path('add_device',views.add_device, name='add_device'),
    path('edit_device/<int:id>', views.edit_device, name='edit_device'),
    path('delete_device/<str:device_ip>',views.delete_device),
    path('device_list/<int:id>', views.current_time, name='current_time'),
    path('access_control',views.access_control, name='access_control'),
    path('door_settings', views.door_setting_list),
    path('department_list', views.department_list, name='department_list'),
    path('department_list/create', views.department_create, name='department_create'),    
    path('department_list/<int:pk>/update', views.department_update, name="department_update"),
    path('department_list/<int:pk>/delete',views.department_delete, name='department_delete'),
    path('users_list/user_create', views.user_create, name='user_create'),
    path('access_control/<str:access_name>/delete', views.access_delete),
    path('access_control/create', views.access_create),
]