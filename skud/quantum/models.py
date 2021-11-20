from django.db import models
from django.db.models.expressions import F

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
    driver_time = models.IntegerField()
    detector_time = models.IntegerField()
    inter_time = models.IntegerField()
    sensor_type = models.CharField(max_length=250)