from django.urls import path
from . import views

app_name = 'quantum'

urlpatterns = [
    # path('', views.PostListView.as_view(), name='post_list'),
    # Сотрудники -----------------------------------------------------------
    path('users_list',views.user_list, name='user_list'),
    path('users_list/user_create', views.user_create, name='user_create'),
    path('user_list/edit/<int:user_id>', views.user_edit, name='user_edit'),
    path('user_list/<int:user_id>/delete', views.user_delete),
    path('users_list/sinc', views.sinc, name='sinc'),
    # -----------------------------------------------------------------------

    # Устройство ------------------------------------------------------------
    path('search_devices_list', views.search_list),
    path('search_devices_list/all', views.search_device_list, name='search_device_list'),
    path('device_list', views.device_list, name='device_list'),
    path('add_device',views.add_device, name='add_device'),
    path('edit_device/<int:id>', views.edit_device, name='edit_device'),
    path('delete_device/<str:device_ip>',views.delete_device),
    path('device_list/<int:id>/time', views.current_time, name='current_time'),
    path('door_settings', views.door_setting_list),
    path('door_settings/door_edit/<int:id>', views.door_edit, name='door_edit'),
    path('door_settings/<int:id>/<str:door_count>/<str:time>', views.door_state_control, name='door_state_control'),
    # path('door_settings/<int:id>/<str:door_count>/<str:time>', views.door_state_control, name='door_state_control'),
    # -------------------------------------------------------------------------



    # Отдел -------------------------------------------------------------------
    path('department_list', views.department_list, name='department_list'),
    path('department_list/create', views.department_create, name='department_create'),    
    path('department_list/<int:pk>/update', views.department_update, name="department_update"),
    path('department_list/<int:pk>/delete',views.department_delete, name='department_delete'),
    # --------------------------------------------------------------------------


    # Уровень доступа ----------------------------------------------------------
    path('access_control',views.access_control, name='access_control'),
    path('access_control/<str:access_name>/delete', views.access_delete),
    path('access_control/create', views.access_create),
    # ---------------------------------------------------------------------------


    # Мониторинг ----------------------------------------------------------------
    path('live_mode', views.monitoring),
    path('live_mode/realtime/<str:ip>', views.monitoring_js),
    # ---------------------------------------------------------------------------

    # Отчет ---------------------------------------------------------------------
    path('reports', views.reports_list),
    path('reports/refresh', views.refresh_report),
    path('reports/smena', views.smena),
    path('reports/grafik', views.grafik),
    path('reports/grafik/new', views.new_grafik),
    path('reports/grafik/<int:id>/delete', views.grafik_delete),
    path('reports/user_grafik', views.user_grafik),
    path('reports/user_grafik/<int:id>', views.getUsers_id, name='getUsers_id'),
    # ---------------------------------------------------------------------------
]