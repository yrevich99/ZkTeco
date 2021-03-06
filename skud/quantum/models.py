from django.db import models
from django.db.models.expressions import F
from django.db.models.fields import CharField, IntegerField
from django.forms import TimeField
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.

class Grafik(models.Model):
    number = models.IntegerField()
    grafik_name = models.CharField(max_length=60,blank=False, unique=True)
    smena = models.CharField(max_length=60,blank=False)
    
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
    keep_open_time = models.CharField(max_length=50)


class Department(MPTTModel):
    name = models.CharField(max_length=64, unique=True, verbose_name="Название Отдела")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Родительская категория")
    class MPTTModel:
        order_insertion_by = ['name']
    
    def __str__(self):
        return self.name

class Access_control(models.Model):
    access_name = models.CharField(max_length=250, unique=True, blank=False)
    lock_control = models.CharField(max_length=250, blank=False)
    time_zone = models.CharField(max_length=250, blank=False)

class User_list(models.Model):
    user_id = models.IntegerField(unique=True)
    images = models.TextField(blank=True)
    surname = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    card_number = models.CharField(max_length=50, unique=True)
    access_id = models.CharField(max_length=150)
    grafik = models.ForeignKey(Grafik, on_delete=models.SET_NULL,blank=True, null=True)
    start_time = models.DateField(blank=True, null=True)
    end_time = models.DateField(blank=True, null=True)


class Id_table(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    # department_id = models.IntegerField(blank=True, null=True)
    access = models.ForeignKey(Access_control, on_delete=models.PROTECT, blank=True, null=True)

class Access_id(models.Model):
    access_id = models.IntegerField(blank=True, null=True)
    device = models.ForeignKey(Devices, on_delete=models.PROTECT)

class Status_access(models.Model):
    user_id = models.CharField(max_length=15)
    user_card = models.CharField(max_length=50)
    access_lock = models.CharField(max_length=15)
    device_ip = models.CharField(max_length=30)
    status_access = models.BooleanField(blank=True, null=True)

class Transactions(models.Model):
    time_second = models.CharField(max_length=60)
    pin = models.IntegerField()
    card_id = models.IntegerField()
    verified = models.CharField(max_length=60)
    door_name = models.CharField(max_length=60)
    event_type = models.CharField(max_length=60)
    in_out_state = models.CharField(max_length=60)
    device_ip = models.CharField(max_length=60)

class Main_report(models.Model):
    user = models.ForeignKey(User_list, on_delete=models.CASCADE)
    user_pin = models.IntegerField()
    data = models.DateField()
    check_time = models.TimeField() 
    in_out_state = models.CharField(max_length=60)
    door_name = models.CharField(max_length=60)

class Door_report(models.Model):
    user = models.ForeignKey(User_list, on_delete=models.CASCADE)
    user_pin = models.IntegerField()
    data = models.DateField()
    check_time = models.TimeField() 
    in_out_state = models.CharField(max_length=60)
    door_name = models.CharField(max_length=60)

class Smena(models.Model):
    smena_name = models.CharField(unique=True, max_length=60)
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_break = models.TimeField()
    end_break = models.TimeField()

