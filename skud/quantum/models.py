from django.db import models
from django.db.models.expressions import F
from django.db.models.fields import CharField, IntegerField
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.

class Devices(models.Model):
    device_name = models.CharField(max_length=250, unique=True, blank=False)
    device_ip = models.CharField(max_length = 15, blank=False, unique=True)
    device_mac = models.CharField(max_length = 150, unique=True)
    serial_number = models.CharField(max_length=250)
    device_type = models.CharField(max_length=20, blank=False)
    device_add = models.CharField(max_length=5, blank=False)
    main_door = models.CharField(max_length = 15, blank=False)
    device_port = models.CharField(max_length = 10,  blank=False)

class Door_setting(models.Model):
    door_number = models.IntegerField()
    name_door = models.CharField(max_length=250, unique=True)
    device_name = models.CharField(max_length=250)
    device_ip = models.CharField(max_length=250)
    driver_time = models.IntegerField()
    detector_time = models.IntegerField()
    inter_time = models.IntegerField()
    sensor_type = models.CharField(max_length=250)


class Department(MPTTModel):
    name = models.CharField(max_length=64, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    class MPTTModel:
        order_insertion_by = ['name']

class Access_control(models.Model):
    access_name = models.CharField(max_length=250, unique=True, blank=False)
    lock_control = models.CharField(max_length=250, blank=False)
    time_zone = models.CharField(max_length=250, blank=False)

class User_list(models.Model):
    user_id = models.IntegerField(unique=True)
    images = models.BinaryField(blank=True)
    surname = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    department_id = models.IntegerField()
    card_number = models.CharField(max_length=50, unique=True)
    access_id = models.CharField(max_length=150)


class Id_table(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    department_id = models.IntegerField(blank=True, null=True)
    access_id = models.IntegerField(blank=True, null=True)

class Access_id(models.Model):
    access_id = models.IntegerField(blank=True, null=True)
    device_id = models.IntegerField(blank=True, null=True)

class Status_access(models.Model):
    user_id = models.CharField(max_length=15)
    user_card = models.CharField(max_length=50)
    access_lock = models.CharField(max_length=15)
    device_ip = models.CharField(max_length=30)
    status_access = models.BooleanField(blank=True, null=True)

