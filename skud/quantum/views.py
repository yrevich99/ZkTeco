from array import array
from asyncio.windows_events import NULL
from concurrent.futures import thread
from email.mime import base
from glob import glob
from msilib.schema import Error, tables
from multiprocessing import context
from re import S, template
import threading
from typing import Dict, Mapping
from urllib import request
from django import http
from django.dispatch import receiver
from django.forms.fields import MultiValueField
from django.template.loader import render_to_string
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from pyzkaccess.exceptions import ZKSDKError
from .models import Devices, Door_setting, Department, Access_control, User_list, Id_table, Access_id, Status_access, Transactions, Main_report, Door_report, Smena, Grafik
from pyzkaccess import ZKAccess, ZK200, ZKSDK, device, door
from pyzkaccess.tables import User, UserAuthorize, Transaction
from .forms import AddDeviceForm, DepartmentForm, CreateAccess, CreateUser, CreateSmena
from datetime import datetime, date, timedelta
import json
from django.views.generic.list import ListView
from threading import Thread, Lock, current_thread
from time import process_time, sleep
from django.core.signals import request_finished
from django.dispatch import receiver
import django.dispatch
from django.db.models import Q
from ast import literal_eval
from operator import itemgetter
import xlwt
import pandas as pd
from bs4 import BeautifulSoup
from django.contrib.staticfiles import finders
from django.contrib import messages
import base64
from io import BytesIO
import os
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
# Create your views here.


def paginations(request,objects, counts):
    paginator = Paginator(objects, counts)
    page = request.GET.get('page')
    try:
        posts = paginator.get_page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return [posts, page]


#????????????????????????---------------------------------------------------------------
def user_list(request):
    users = User_list.objects.all()
    # pag = paginations(request, users, 10)
    # posts = pag[0]
    # page = pag[1]
    return render(request, 'skud/views/users_list.html', {'users': users})

def user_create(request):
    try:
        ids =  User_list.objects.all().last().user_id
        ids += 1
    except:
        ids = 1
            
    form = CreateUser(request.POST)
    if request.method == 'POST':
        # if form.is_valid():
        new_user = User_list()
        # id_table = Id_table()
        new_user.user_id = request.POST['userId']
        new_user.surname = request.POST['surname']
        new_user.name = request.POST['name']
        new_user.department_id = request.POST['department']
        new_user.card_number = request.POST['card_number']

        # file = open(request.POST['images'], 'bw')
        # print(file)
        # new_user.images = file
        if request.POST['images']:
            new_user.images = request.POST['images']


        try:
            access_list =  list(set(request.POST.getlist('access')))
            access_str = ''
            for value in access_list:
                if Access_control.objects.filter(id=value):
                    if access_str == '':
                        access_str += f'{Access_control.objects.get(id=value).access_name}'
                    else:
                        access_str += f';{Access_control.objects.get(id=value).access_name}'
                    lock_control = Access_control.objects.get(id=value).lock_control
                    set_access_user(lock=lock_control, card=request.POST['card_number'], id=request.POST['userId'])
                id_tables = Id_table()
                id_tables.user_id = request.POST['userId']
                id_tables.access_id = value
                id_tables.save()
            new_user.access_id = access_str
        except Exception as err:
            print(err)
            new_user.access_id = request.POST.get('access', '')
        new_user.save()
        return  HttpResponseRedirect('/users_list')

    return render(request, 'skud/views/user_create.html', {
                'departments': Department.objects.all(),
                'access_levels': Access_control.objects.all(),
                'user_id': ids
                })

def user_edit(request, user_id):
    user = User_list.objects.get(user_id=user_id)
    if request.method == 'POST':
        try:
            access_list =  list(set(request.POST.getlist('access'))) 
            acc = Id_table.objects.filter(user_id=user_id).values('access_id')
            old_access = []
            for item in acc:
                for i in item.values():
                    old_access.append(str(i)) 
            access_str = ''
            del_access = [access for access in old_access if access not in access_list]
            add_access = [access for access in access_list if access not in old_access]
            if user.card_number == request.POST['card_number']:
                for value in del_access:
                    lock_control = Access_control.objects.get(id=value).lock_control
                    del_access_user(lock=lock_control, card=request.POST['card_number'], id=request.POST['userId'])
                    id_tables = Id_table.objects.filter(Q(user_id=user_id) & Q(access_id=value)).delete()
                for value in add_access:
                    lock_control = Access_control.objects.get(id=value).lock_control
                    set_access_user(lock=lock_control, card=request.POST['card_number'], id=request.POST['userId'])

                    id_tables = Id_table()
                    id_tables.user_id = request.POST['userId']
                    id_tables.access_id = value
                    id_tables.save()

            elif user.card_number != request.POST['card_number']:
                for value in old_access:
                    lock_control = Access_control.objects.get(id=value).lock_control
                    del_access_user(lock=lock_control, card=user.card_number, id=request.POST['userId'])
                    id_tables = Id_table.objects.filter(Q(user_id=user_id) & Q(access_id=value)).delete()
                for value in access_list:
                    lock_control = Access_control.objects.get(id=value).lock_control
                    set_access_user(lock=lock_control, card=request.POST['card_number'], id=request.POST['userId'])

                    id_tables = Id_table()
                    id_tables.user_id = request.POST['userId']
                    id_tables.access_id = value
                    id_tables.save()

            for value in access_list:
                if Access_control.objects.filter(id=value):
                    if access_str == '':
                        access_str += f'{Access_control.objects.get(id=value).access_name}'
                    else:
                        access_str += f';{Access_control.objects.get(id=value).access_name}'
            user.access_id = access_str
            user.card_number = request.POST['card_number']
            if request.POST['images']:
                user.images = request.POST['images']
            messages.success(request, '?????????????? ????????????????!')
        except Exception as err:
            messages.error(request, '????????????.')
            print(err)

        user.surname = request.POST['surname']
        user.name = request.POST['name']
        user.department_id = request.POST['department']
        user.save()
        # return HttpResponseRedirect('/users_list')

    return render(request, 'skud/views/user_edit.html',{
                'user': user,
                'departments': Department.objects.all(),
                'access_levels': Access_control.objects.all(),
                'user_access': Id_table.objects.filter(user_id=user_id),
                })


def user_delete(request,user_id):
    try:
        user_list = get_object_or_404(User_list, user_id=user_id)
        if user_list.access_id != '':
            access_list = user_list.access_id.split(';')
            for i in access_list:
                if Access_control.objects.get(access_name=i):
                    lock_list = Access_control.objects.get(access_name=i).lock_control
                    print(lock_list)
                    del_user_access = del_access_user(id=str(user_list.user_id), card=user_list.card_number, lock=lock_list)
                else:
                    print('Error')
        user_list.delete()
        user_table = Id_table.objects.filter(user_id=user_id).delete()
        messages.success(request, '?????????????? ??????????????!')
        return  HttpResponseRedirect('/users_list')
    except Exception as err:
        print(err)
        messages.error(request, '?????????????????? ????????????!')
        return  HttpResponseRedirect('/users_list')



def set_access_user(id: str,card,lock, record=True):
    ip_and_access = lock.split(';')
    print(ip_and_access)
    for item in ip_and_access:
        print(item)
        key_and_value = item.split(',')
        ip = key_and_value[0]
        access = int(key_and_value[1])
        try:
            zk = ZKAccess(f'protocol=TCP,ipaddress={ip},port=4370,timeout=4000,passwd=')
            set_user = User(card=card, pin=id).with_zk(zk)
            set_user.save()
            set_auth = UserAuthorize(pin=id, timezone_id=1, doors=access).with_zk(zk)
            set_auth.save()
            print('success add')
            if record == False:
                return True
        except Exception as err:
            if record == True:
                status = Status_access()
                status.user_id = id
                status.user_card = card
                status.access_lock = access
                status.device_ip = ip
                status.status_access = True
                status.save()
                print('set - ',err)
            

def del_access_user(id: str,card,lock, record=True):
    ip_and_access = lock.split(';')
    for item in ip_and_access:
        key_and_value = item.split(',')
        ip = key_and_value[0]
        access = int(key_and_value[1])
        try:
            zk = ZKAccess(f'protocol=TCP,ipaddress={ip},port=4370,timeout=4000,passwd=')
            set_user = User(card=card, pin=id).with_zk(zk)
            set_user.delete()
            set_auth = UserAuthorize(pin=id, timezone_id=1, doors=access).with_zk(zk)
            set_auth.delete()
            print('success delete')
            if record == False:
                return True
        except Exception as err:
            if record == True:
                status = Status_access()
                status.user_id = id
                status.user_card = card
                status.access_lock = access
                status.device_ip = ip
                status.status_access = False
                status.save()
                print('del - ',err)
            # elif record == False:
            #     print('del - ',err)
            #     yield False

def sinc(request):
    access = Status_access.objects.all()
    for item in access:
        if item.status_access == True:
            ret_access = set_access_user(item.user_id, item.user_card, f'{item.device_ip},{item.access_lock}', record=False)
            if ret_access == True:
                item.delete()
        elif item.status_access == False:
            ret_access = del_access_user(item.user_id, item.user_card, f'{item.device_ip},{item.access_lock}', record=False)
            if ret_access == True:
                item.delete()
    messages.success(request, '?????????????? ????????????????????????????????!')
    return  HttpResponseRedirect('/users_list')

#-------------------------------------------------------------------------------------

#??????????-----------------------------------------------------------
def department_list(request):
    return render(request, 'skud/views/department/department_list.html', {'department':Department.objects.all()})

def save_department_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            department = Department.objects.all()
            data['html_department_list'] = render_to_string('skud/views/department/department_list.html', {
                'department': department
            })
        else:
            data['form_is_valid'] = False
    
    context = {'form': form, 'parent':Department.objects.all()}    
    data['html_form'] = render_to_string(template_name,
        context,
        request=request,
    )
    return JsonResponse(data)

def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
    else:
        form = DepartmentForm()
    return save_department_form(request, form, 'skud/views/department/add_department.html')

def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
    else:
        form = DepartmentForm(instance=department)
    return save_department_form(request, form, 'skud/views/department/department_update.html')

def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    data = dict()
    if request.method == 'POST':
        department.delete()
        data['form_is_valid'] = True
        # data['html_department_list'] = render_to_string('skud/views/department/department_list.html',
        # {'departments': Department.objects.all()}
        # )
    else:
        context = {'department':department}
        data['html_form'] = render_to_string('skud/views/department/department_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)
#--------------------------------------------------------------------------------

#??????????-------------------------------------------------------------------------------------
def door_setting_list(request):
    return render(request, 'skud/views/door_setting.html', {'doors': Door_setting.objects.all()})



def door_edit(request, id):
    data = dict()
    if request.method == 'POST':
        door = Door_setting.objects.get(id=id)
        door.name_door = request.POST['name_door']
        try:
            sensor_type = ''
            # if (request.POST['sensor_type'] == '???? ??????????????'):
            #     sensor_type = 0
            # elif (request.POST['sensor_type'] == '??????????????????-????????????????'):
            #     sensor_type = 1
            # elif (request.POST['sensor_type'] == '??????????????????-????????????????'):
            #     sensor_type = 2
            # if (request.POST['sensor_type'] == '0'):
            #     sensor_type = '???? ??????????????'
            # elif (request.POST['sensor_type'] == '1'):
            #     sensor_type = '?????????????????? - ????????????????'
            # elif (request.POST['sensor_type'] == '2'):
            #     sensor_type = '?????????????????? - ????????????????'
            parameters_set = {
            f"Door{door.door_number}Drivertime":f"{request.POST['driver_time']}",
            f"Door{door.door_number}Detectortime":f"{request.POST['detector_time']}",
            f"Door{door.door_number}Intertime":f"{request.POST['inter_time']}",
            f"Door{door.door_number}SensorType": f"{request.POST['sensor_type']}",
            f"Door{door.door_number}KeepOpenTimeZone": f"{request.POST['keep_open_time']}",
            }
            parameters_get = f'Door{door.door_number}Drivertime,Door{door.door_number}Detectortime,Door{door.door_number}Intertime,Door{door.door_number}SensorType,Door{door.door_number}KeepOpenTimeZone'
            
            set_param = DeviceSetting().door_setting_set(door.device_ip,'4370',parameters_set)
            get_param = DeviceSetting().door_setting_get(door.device_ip,'4370',parameters_get)
            print(get_param)
            if (get_param[f'Door{door.door_number}SensorType'] == '0'):
                sensor_type = '???? ??????????????'
            elif (get_param[f'Door{door.door_number}SensorType'] == '1'):
                sensor_type = '?????????????????? - ????????????????'
            elif (get_param[f'Door{door.door_number}SensorType'] == '2'):
                sensor_type = '?????????????????? - ????????????????'
            door.driver_time = int(get_param[f'Door{door.door_number}Drivertime'])
            door.detector_time = int(get_param[f'Door{door.door_number}Detectortime'])
            door.inter_time = int(get_param[f'Door{door.door_number}Intertime'])
            door.sensor_type = sensor_type

            if get_param[f'Door{door.door_number}KeepOpenTimeZone'] == '0':
                door.keep_open_time = ' '
            elif get_param[f'Door{door.door_number}KeepOpenTimeZone'] == '1':
                door.keep_open_time = '????????????????'
            messages.success(request, '?????????????? ????????????????!')
        except Exception as err:
            print('errSet',err)
            messages.error(request, '???????????? ???????????????? ???? ??????????????!')
        door.save()
        
    context = {'door': Door_setting.objects.get(id=id)}
    data['html_form'] = render_to_string('skud/views/door_edit.html',
    context,
    request=request)
    return JsonResponse(data)

def door_state_control(request,id,door_count, time):
    door = Door_setting.objects.get(id=id)
    try:
        
        
        # connstr = f"protocol=TCP,ipaddress={door.device_ip},port=4370,timeout=4000,passwd="
        # with ZKAccess(connstr=connstr) as zk:
        #     zk.doors[0].relays.switch_on(5)
        if time == '255':
            message_time = f'?????????? {door.name_door} ??????????????'
            state_status = 'open'
        elif time == '0':
            message_time = f'?????????? {door.name_door} ??????????????'
            state_status = 'close'
        state = DeviceSetting().open_close_door(door.device_ip,'4370',door_count, time, state_status)
        messages.success(request, message_time)
    except Exception as err:
        print(err)
        
        if time == '255':
            message_time = f'?????????? {door.name_door} ?????????????? ???? ??????????????'
        elif time == '0':
            message_time = f'?????????? {door.name_door} ?????????????? ???? ??????????????'
        messages.error(request, message_time)
    
    return HttpResponseRedirect('/door_settings')
#-------------------------------------------------------------------------------------------------------

#????????????????????----------------------------------------------------------------------------

class DeviceSetting():
    
    def __init__(self) -> None:
        pass

    def door_setting_get(self,ip,port,parametrs):
        try:
            conn = f"protocol=TCP,ipaddress={ip},port={port},timeout=4000,passwd="
            params = parametrs.split(',')
            connects = ZKSDK('plcommpro.dll')
            connects.connect(conn)
            door_get = connects.get_device_param(params,2048)
            connects.disconnect()
            return door_get
        except Exception as err:
            return err

    def door_setting_set(self,ip,port,parametrs):
        conn = f"protocol=TCP,ipaddress={ip},port={port},timeout=4000,passwd="
        connects = ZKSDK('plcommpro.dll')
        connects.connect(conn)
        door_get = connects.set_device_param(parametrs)
        connects.disconnect()

    def open_close_door(self,ip,port,door_count,time, state_status):
        conn = f"protocol=TCP,ipaddress={ip},port={port},timeout=4000,passwd="
        connects = ZKSDK('plcommpro.dll')
        connects.connect(conn)
        door_count = int(door_count)
        time = int(time)
        if state_status == 'open':
            state = connects.control_device(1,door_count,1,time,0)
        elif state_status == 'close':
            state = connects.control_device(4,door_count,0,0,0)
        connects.disconnect()


    
    def search_devices(self):
        results = []
        device_counts = 0
        
        try:
            found = ZKSDK('plcommpro.dll').search_device('255.255.255.255',4096)
            device_counts = len(found)
            for device_count in range(0, device_counts):
                copy_found = found[device_count-1].split(',')
                results_copys = {}
                results_copys['num'] = str(device_count+1)

                for founds in copy_found:
                    key, value = founds.split('=')

                    if key == 'MAC' or key == 'IP' or key == 'SN' or key == 'Device':
                        results_copys[key] = value
                add_device = Devices.objects.filter(serial_number=results_copys['SN'])

                if add_device:
                    results_copys['adds'] = '????'
                else:
                    results_copys['adds'] = '??????'

                results.append(results_copys)
                del results_copys  
            return [results,device_counts]
        except Exception as err:
            print(err)
            return 'error'

    def ip_search(self,ip):
        found = ZKSDK('plcommpro.dll').search_device(ip,4096)
        device_counts = len(found)
        copy_found = found[0].split(',')
        results_copys = {}

        for founds in copy_found:
            key, value = founds.split('=')

            if key == 'MAC' or key == 'IP' or key == 'SN' or key == 'Device':
                results_copys[key] = value
        return results_copys

def search_list(request):
    return render(request, 'skud/views/search_device.html')

def search_device_list(request):
    search = DeviceSetting().search_devices()
    if(search != 'error'):
        results = search[0]
        device_counts = search[1]
    else:
        results = {}
        device_counts = 0
    return render(request, 'skud/views/search_device.html', {
                                                            'results': results,
                                                            'device_counts': device_counts,
                                                            })

def modify_ip(request):
    return JsonResponse()

def device_list(request):
    return render(request, 'skud/views/all_device.html', {'devices': Devices.objects.all()})

def add_device(request):
    form = AddDeviceForm(request.POST)
    if request.method == 'POST':
        try:
            if form.is_valid():
                ip = request.POST['device_ip']
                port = request.POST['device_port']
                connstr = f'protocol=TCP,ipaddress={ip},port={port},timeout=4000,passwd='
                dev = DeviceSetting().ip_search(ip)

                # live = LiveStream(ip=ip)
                # live.door4todoor2({'Door4ToDoor2':request.POST['todoor']})


                # ???????????????????? ???????????????????? ---------------------------------------------------------
                add_device = Devices()
                add_device.device_name = request.POST['device_name']
                add_device.device_ip = request.POST['device_ip']
                add_device.device_port = request.POST['device_port']
                add_device.device_add = '????'
                add_device.device_mac = dev['MAC']
                add_device.device_type = dev['Device']
                add_device.serial_number = dev['SN']
                if request.POST.get('main_door'):
                    add_device.main_door = '????'
                else:
                    add_device.main_door = '??????'
                if request.POST.get('device_clear'):
                    zk = ZKAccess(f'protocol=TCP,ipaddress={request.POST["device_ip"]},port=4370,timeout=4000,passwd=')
                    for record in zk.table('User'):
                        record.delete()
                    for record in zk.table('UserAuthorize'):
                        record.delete()
                    print('delete')
                add_device.save()

                # ???????????????????? ??????????--------------------------------------------------------
                lock_count = DeviceSetting().door_setting_get(ip,port,"LockCount")
                lock_count = int(lock_count["LockCount"])
                
                for counts in range(1,(lock_count+1)):
                    parameters = f'Door{counts}Drivertime,Door{counts}Detectortime,Door{counts}Intertime,Door{counts}SensorType,Door{counts}KeepOpenTimeZone'
                    door_setting = Door_setting()
                    get_param = DeviceSetting().door_setting_get(ip,port,parameters)
                    door_setting.door_number = counts
                    door_setting.device_ip = request.POST['device_ip']
                    door_setting.name_door = (request.POST['device_name'] + '-' + str(counts))
                    door_setting.device_name = request.POST['device_name']
                    door_setting.driver_time = int(get_param[f'Door{counts}Drivertime'])
                    door_setting.detector_time = int(get_param[f'Door{counts}Detectortime'])
                    door_setting.inter_time = int(get_param[f'Door{counts}Intertime'])
                    if get_param[f'Door{counts}KeepOpenTimeZone'] == '0':
                        door_setting.keep_open_time = ' '
                    elif get_param[f'Door{counts}KeepOpenTimeZone'] == '1':
                        door_setting.keep_open_time = '????????????????'
                    if (int(get_param[f'Door{counts}SensorType']) == 0):
                        door_setting.sensor_type = '???? ??????????????'
                    elif (int(get_param[f'Door{counts}SensorType']) == 1):
                        door_setting.sensor_type = '?????????????????? - ????????????????'
                    elif (int(get_param[f'Door{counts}SensorType']) == 2):
                        door_setting.sensor_type = '?????????????????? - ????????????????'
                    door_setting.save()
                # ------------------------------------------------------------------------------
            messages.success(request, '?????????????? ??????????????????!')
            return HttpResponseRedirect('/device_list')
        except ZKSDKError as err:
            print(err)
            messages.error(request, '???????????? ????????????????????')
        except Exception as err:
            print(err)
            messages.error(request, '???????????????? ????????????') 
    return render(request, 'skud/views/add_device.html')

def edit_device(request, id):
    if request.method == 'POST':
        try:
            device = Devices.objects.get(id=id)
            door = Door_setting.objects.filter(device_name=device.device_name)
            
            for counts in range(0, len(door)):
                door[counts].device_name = request.POST['device_name']
                door[counts].save()
            live = LiveStream(ip=request.POST['device_ip'])
            live.door4todoor2({'Door4ToDoor2':request.POST['todoor']})

            device.device_name = request.POST['device_name']
            device.save()
            messages.success(request, '?????????????? ????????????????') 
        except Exception as err:
            print(err)
            messages.error(request, '???????????? ???? ????????????') 
        return HttpResponseRedirect('/device_list')
    data = {
        'device' : Devices.objects.get(id=id)
    }
    return render(request, 'skud/views/add_device.html', context=data)

def delete_device(request, device_ip):
    try:
        if (Devices.objects.get(device_ip=device_ip)):
            dev_name = Devices.objects.get(device_ip=device_ip).device_name
            device = get_object_or_404(Devices, device_ip=device_ip).delete()
            door_setting = Door_setting.objects.filter(device_name=dev_name).delete()
    except Exception as err:
        print(err)
        messages.error(request, '???? ?????????????? ??????????????') 
    return HttpResponseRedirect('/device_list')



def current_time(request, id):
    data = dict()
    try:
        device = Devices.objects.get(id=id)
        connstr = f'protocol=TCP,ipaddress={device.device_ip},port={device.device_port},timeout=4000,passwd='
        with ZKAccess(connstr=connstr) as zk:
            zk.parameters.datetime = datetime.now()
            message_time = '?????????? ??????????????????????'
        data['message'] = message_time
    except Exception as err:
        print(err)
        message_time = '???? ?????????????? ???????????????????? ??????????'
        data['message'] = message_time
        
    return JsonResponse(data)
#---------------------------------------------------------------------


#????????????-----------------------------------------------------------------------------------
def access_control(request):
    return render(request, 'skud/views/access_control.html', {'access_control':Access_control.objects.all()})

def access_delete(request,access_name):
    try:
        access = get_object_or_404(Access_control, access_name=access_name)
        access_id = Access_id.objects.filter(access_id=access.id)
        print(access_id)
        access_id.delete()
        access.delete()
        messages.success(request, '?????????????? ??????????????')
        return  HttpResponseRedirect('/access_control')
    except Exception as err:
        messages.error(request, '???????????????????? ?????????????? ?????? ?????? ?? ???????????????????????? ???????? ???????????? ????????????')

def access_create(request):
    form = CreateAccess(request.POST)
    if request.method == 'POST':
        try:
            if form.is_valid():
                lock_list = set(request.POST.getlist('lock_control'))
                lock_dict = {}
                strings = ''
                access = Access_control()

                for value in lock_list:
                    lock_split = value.split('|||')
                    if lock_split[0] not in lock_dict.keys():
                        lock_dict[lock_split[0]] = []
                        lock_dict[lock_split[0]].append(lock_split[1])
                    elif lock_split[0] in lock_dict.keys():
                        lock_dict[lock_split[0]].append(lock_split[1])
                for key, value in lock_dict.items():
                    dec = [0,0,0,0]
                    for val in value:
                        if val == '1':
                            dec[3] = 1
                        elif val == '2':
                            dec[2] = 1
                        elif val == '3':
                            dec[1] = 1
                        elif val == '4':
                            dec[0] = 1
                    decoding  = int(f"{dec[0]}{dec[1]}{dec[2]}{dec[3]}",2)
                    lock_dict[key] = decoding
                    if strings == '':
                        strings = f'{key},{decoding}'
                    else:
                        strings += f';{key},{decoding}'

                access.access_name = request.POST['access_name']
                access.lock_control = strings
                access.time_zone = request.POST['time_zone']
                access.save()
                try:
                    for key in lock_dict.keys():
                        acc_id = Access_id()
                        acc_id.access_id = access.id
                        if Devices.objects.get(device_ip=key):
                            acc_id.device_id = Devices.objects.get(device_ip=key).id
                        acc_id.save()
                except Exception as err:
                    print(err)
                
                return HttpResponseRedirect('/access_control')
        except Exception as err:
            print(err)
    return render(request, 'skud/views/access_control_create.html', {'doors': Door_setting.objects.all()})
#----------------------------------------------------------------------------------------------------


#????????????????????------------------------------------------------------------------------------
class LiveStream():
    def __init__(self,ip) -> None:
        self.ip = ip

    def door4todoor2(self,param):
        conn = f"protocol=TCP,ipaddress={self.ip},port=4370,timeout=4000,passwd="
        connects = ZKSDK('plcommpro.dll')
        connects.connect(conn)
        todoor = connects.set_device_param(param)
        connects.disconnect()

    def convert_date(self, time):
        time = int(time)
        Second = time  %  60
        Minute = int(( time / 60 ) % 60)
        Hour =  int(( time / 3600 ) % 24)
        Day = int(( time / 86400 )  %  31 + 1)
        Month= int(( time / 2678400 ) % 12 + 1)
        Year = int((time / 32140800 ) + 2000)
        datetime_object = datetime.strptime(f'{Year}-{Month}-{Day} {Hour}:{Minute}:{Second}', "%Y-%m-%d %H:%M:%S")
        return datetime_object

    def verify_mode(self,num):
        verify = {
            '1': '??????????????????',
            '3': '????????????',
            '4': '??????????',
            '6': '?????????? ?????? ??????????????????',
            '10': '?????????? ?? ??????????????????',
            '11': '?????????? ?? ????????????',
            '200': '????????????'
        }
        if num in verify:
            return verify[num]
        else:
            return '????????????'
        
    def door_name(self, door_id):
        if door_id == '0':
            return ''
        else:
            try:
                return Door_setting.objects.get(device_ip=self.ip,door_number=int(door_id)).name_door
            except Exception as err:
                print(err)

    def in_out_state(self,state):
        status = {
            '0': '????????',
            '1': '??????????',
            '2': '????????????????????'
        }
        if state in status:
            return status[state]
        else:
            return 'Unknown'

    def event_type(self, event):
        event_list = {
            '0': '???????????????? ????????????',
            '1': '???????????????????? ???????????????? ???? ?????????????????? ????????',
            '2': '???????????????? ???????????????????? ????????????????????????(??????????)',
            '3': '?????????????? ?????????????????? ????????????????(??????????)',
            '4': '?????????????? ?????????????????? ?????????????? ',
            '5': '?????????????? ?? ?????????????? ?????????????? ??????????',
            '6': '???????????????????????????? ?????????????? ??????????',
            '7': '???????????? ???????????????????? ??????????????',
            '8': '?????????????????????????? ????????????????',
            '9': '?????????????????????????? ????????????????',
            '10': '?????????????????? ?????????????????????????? ??????????????',
            '11': '???????????????? ?????????????????????????? ??????????????',
            '12': '???????????? AUX ??????????',
            '13': '???????????? AUX ??????????',
            '14': '?????????????? ????????????????????',
            '15': '?????????????? ?????????????????? ????????????????(??????????????????)',
            '16': '?????????????? ????????????????????',
            '17': '?????????????? ???????????? + ??????????????????',
            '18': '???????????????? ???????????????????? ????????????????????????(?????????????????????? ????????????)',
            '19': '???????????????? ???????????????????? ????????????????????????(?????????? + ?????????????????? ????????????)',
            '20': '?????????????? ???????????????? ???????????????? ?????????? ??????????????????',
            '21': '?????????????? ???????? ?????????? ??????????????????',
            '22': '???????????????????? ?????????????? ????????',
            '23': '???????????? ????????????????',
            '24': '???????????? ???? ?????????????????? ??????????????',
            '25': '????????????????????',
            '26': '???????????????????????????? ?? ???????????????????????????? ???????????????????? ????????',
            '27': '???????????????????????????????????????? ??????????',
            '28': '?????????? ???????????????? ?????????????? ?????????? ????????????????',
            '29': '???????? ???????????????? ?????????? ??????????',
            '30': '???????????? ????????????',
            '31': '?????????????? ???????????????? ???????????????? ?????????????? ?????????????????? ????????????',
            '32': '???????????????????????????? ?? ?????????????? ???????????????????? ???????? (?????????????????? ????????????)',
            '33': '???????? ???????????????? ?????????????????? ???????????? ??????????',
            '34': '???????????????????????????????????????? ?????????????????? ????????????',
            '35': '?????????????? ???????? ?????????? ?????????????????? (?????????????????? ????????????)',
            '36': '?????????????? ???????? ?????????? ?????????????????? (???????????? ????????????)',
            '37': '???? ?????????????? ?????????????? ??????????',
            '101': '???????????? ???????????????????????????? ?????????????? ',
            '102': '?????????? ?????????????????? ????????????????',
            '103': '???????????????????????? ???????????????? ???????????????????? ????????????',
            '200': '?????????? ?????????????????? ??????????????????',
            '201': '?????????? ?????????????? ??????????????????',
            '202': '?????????? ?????????????? ?????????????? ',
            '203': '???????????????? ???????????????? ????????????????',
            '204': '???????????????????? ????????????????',
            '205': '?????????????????? ????????????????',
            '206': '???????????? ????????????????????',
            '220': '?????????????????????????????? ???????? ????????????????',
            '221': '?????????????????????????????? ???????? ??????????????????',
            '255': '???????????? ?????????? ?? ???????????? ????????????????????????',
        }
        if event in event_list:
            return event_list[event]
        else:
            return 'Unknown'

    def user_auth(self, card):
        user = {}
        try:
            if card == User_list.objects.get(card_number=card).card_number:
                user['surname'] =  User_list.objects.get(card_number=card).surname
                user['name'] = User_list.objects.get(card_number=card).name
        except Exception as err:
            user['surname'] = ''
            user['name'] = '???????????????????????????????????????? ????????????????????????'
        return user



    def transaction(self):
        conn = f'protocol=TCP,ipaddress={self.ip},port=4370,timeout=4000,passwd='
        zk = ZKAccess(conn)
        tables = zk.table('Transaction')
        if tables.count() > 0:
            for i in range(tables.count()):
                transaction = Transactions()
                transaction.card_id  = tables[i].raw_data['Cardno']
                transaction.pin = tables[i].raw_data['Pin']
                transaction.verified = self.verify_mode(tables[i].raw_data['Verified'])
                transaction.door_name = self.door_name(tables[i].raw_data['DoorID']) 
                transaction.event_type = self.event_type(tables[i].raw_data['EventType']) 
                transaction.in_out_state = self.in_out_state(tables[i].raw_data['InOutState']) 
                transaction.time_second = self.convert_date(tables[i].raw_data['Time_second']) 
                transaction.device_ip = self.ip
                transaction.save()
        else:
            return False
    
    def reports(self):
        try:
            conn = f'protocol=TCP,ipaddress={self.ip},port=4370,timeout=4000,passwd='
            zk = ZKAccess(conn)
            tables = zk.table('Transaction')
            if tables.count() > 0:
                for i in range(tables.count()):
                    try:
                        user = User_list.objects.get(user_id=int(tables[i].raw_data['Pin']))
                        if user.user_id == int(tables[i].raw_data['Pin']):
                            datatime = str(self.convert_date(tables[i].raw_data['Time_second'])).split(' ')
                            if Devices.objects.get(device_ip=self.ip).main_door == '????':
                                report = Main_report()
                                report.user_id = user.id
                                report.user_pin = int(tables[i].raw_data['Pin'])
                                report.data = datatime[0]
                                report.check_time = datatime[1]
                                report.in_out_state = self.in_out_state(tables[i].raw_data['InOutState'])
                                report.door_name = self.door_name(tables[i].raw_data['DoorID'])
                                report.save()
                                tables[i].delete()
                            elif Devices.objects.get(device_ip=self.ip).main_door == '??????':
                                report = Door_report()
                                report.user_id = user.id
                                report.user_pin = int(tables[i].raw_data['Pin'])
                                report.data = datatime[0]
                                report.check_time = datatime[1]
                                report.in_out_state = self.in_out_state(tables[i].raw_data['InOutState'])
                                report.door_name = self.door_name(tables[i].raw_data['DoorID'])
                                report.save()
                                tables[i].delete()
                        else:
                            continue
                    except Exception as err:
                        print(err)
        except Exception as err:
            print(err)


    def live_mode(self):
        conn = f'protocol=TCP,ipaddress={self.ip},port=4370,timeout=4000,passwd='
        tables = []
        zk = ZKSDK('plcommpro.dll')
        zk.connect(conn)
        rt_logs = zk.get_rt_log(256)
        print(rt_logs)
        for rt_log in rt_logs:
            table = {}
            item = rt_log.split(',')
            if item[4] == '255':
                continue
            else:
                table['time'] = item[0]
                table['pin'] = item[1]
                table['surname'] = self.user_auth(item[2])['surname']
                table['name'] = self.user_auth(item[2])['name']
                table['card'] = item[2]
                table['door'] = self.door_name(item[3]) 
                table['event'] = self.event_type(item[4]) 
                table['entry_exit'] = self.in_out_state(item[5]) 
                table['verify'] = self.verify_mode(item[6]) 
                tables.append(table)
        zk.disconnect()
        # tables = [{'time': '2022-02-05 16:37:42', 'pin': '1', 'surname': '', 'name': '??????????', 'card': '3545531', 'door': '4', 'event': '0', 'entry_exit': '0', 'verify': '6'},
        #         {'time': '2022-02-05 16:37:42', 'pin': '0', 'surname': '', 'name': '??????????', 'card': '0', 'door': '4', 'event': '27', 'entry_exit': '0', 'verify': '6'},
        #         {'time': '2022-02-05 16:37:43', 'pin': '1', 'surname': '', 'name': '??????????', 'card': '3545531', 'door': '4', 'event': '0', 'entry_exit': '0', 'verify': '6'}, 
        #         {'time': '2022-02-05 16:37:44', 'pin': '0', 'surname': '', 'name': '??????????', 'card': '0', 'door': '4', 'event': '27', 'entry_exit': '0', 'verify': '6'},
        #         {'time': '2022-02-05 16:37:45', 'pin': '1', 'surname': '', 'name': '??????????', 'card': '3545531', 'door': '4', 'event': '0', 'entry_exit': '0', 'verify': '6'}]
        print(self.ip)
        return tables
        




def monitoring(request):
    return render(request, 'skud/views/monitoring.html', {'device': Devices.objects.all()})


def monitoring_js(request, ip):
    data = dict()
    data['real'] = LiveStream(ip).live_mode()
    context = {'dates': data['real']}
    return JsonResponse(data)
# ---------------------------------------------------------------------------------------


# ?????????? ------------------------------------------------------------------------------------------
def reports_list(request):
    if request.method == 'GET':
        return render(request, 'skud/views/reports/report.html') 
    if request.method == 'POST':
        reports = AllReports(datetime.strptime(request.POST['start_time'], "%Y-%m-%d").date(), datetime.strptime(request.POST['end_time'], "%Y-%m-%d").date())
        user_list = []
        context = {'reports': user_list, 
                'to_filter': request.POST['filter'], 
                'to_department': int(request.POST['department']), 
                'to_start_time': request.POST['start_time'], 
                'to_end_time': request.POST['end_time'],
                }
        if request.POST['department'] != '0':  
            users_all = User_list.objects.filter(department=request.POST['department'])
        else:
            users_all = User_list.objects.all()

        if request.POST['filter'] == '5':
            # ???????????????? ????????????????
            if request.POST['department'] != '0':
                return render(request, 'skud/views/reports/filter/all_reports.html', 
                {'main_report': Main_report.objects.filter(data__range=[request.POST['start_time'],request.POST['end_time']], user__department=request.POST['department']),
                'reports': user_list, 
                'to_filter': request.POST['filter'], 
                'to_department': int(request.POST['department']), 
                'to_start_time': request.POST['start_time'], 
                'to_end_time': request.POST['end_time'],})
            else:
                return render(request, 'skud/views/reports/filter/all_reports.html', 
                {'main_report': Main_report.objects.filter(data__range=[request.POST['start_time'],request.POST['end_time']]),
                'reports': user_list, 
                'to_filter': request.POST['filter'], 
                'to_department': int(request.POST['department']), 
                'to_start_time': request.POST['start_time'], 
                'to_end_time': request.POST['end_time'],})

        if request.POST['filter'] == '2':
            # ???????????? ????????????????????
            for user in users_all:
                if user.grafik:
                    if reports.start(request.POST['filter'], user):
                        user_list += reports.start(request.POST['filter'], user)
            return render(request, 'skud/views/reports/filter/latecomers.html', context)

        if request.POST['filter'] == '3':
            # ???????????? ????????
            for user in users_all:
                if user.grafik:
                    if reports.start(request.POST['filter'], user):
                        user_list += reports.start(request.POST['filter'], user)
            return render(request, 'skud/views/reports/filter/earlyCare.html', context)

        if request.POST['filter'] == '4':
            # ??????????????????????????
            for user in users_all:
                if user.grafik:
                    if reports.start(request.POST['filter'], user):
                        user_list += reports.start(request.POST['filter'], user)
            return render(request, 'skud/views/reports/filter/missing.html', context)

        if request.POST['filter'] == '1':
            # ???????????? ??????????????????????
            for user in users_all:
                if user.grafik:
                    if reports.start(request.POST['filter'], user):
                        user_list += reports.start(request.POST['filter'], user)
            return render(request, 'skud/views/reports/filter/employee_schedule.html', context)

        if request.POST['filter'] == '6':
            # ?????????? ??????????????
            for user in users_all:
                if user.grafik:
                    if reports.start(request.POST['filter'], user):
                        user_list += reports.start(request.POST['filter'], user)
            return render(request, 'skud/views/reports/filter/work_time.html', context)

def refresh_report(request):
    query = Devices.objects.all()
    for ip in query:
        live = LiveStream(ip.device_ip)
        live.reports()
    return HttpResponseRedirect('/reports')

def smena(request):
    form = CreateSmena(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            smena = Smena()
            smena.smena_name = request.POST['smena_name']
            smena.start_time = request.POST['start_time']
            smena.end_time = request.POST['end_time']
            smena.start_break = request.POST['start_break']
            smena.end_break = request.POST['end_break']
            smena.save()
            return HttpResponseRedirect('/reports/smena')
    return render(request, 'skud/views/reports/smena.html', {'time_now': datetime.now().time().strftime ("%H:%m"), 'smena': Smena.objects.all()})

def grafik(request):
    if request.method == 'POST':
        try:
            grafik = Grafik.objects.get(id=request.POST['grafik_id'])
            grafik.number = request.POST['start_time']
            grafik.grafik_name = request.POST['grafik_name']
            smena_data = ''
            for number in range(0,int(request.POST['start_time'])):
                if smena_data == '':
                    smena_data += request.POST[f'filter_{number}']
                else:
                    smena_data += ',' + request.POST[f'filter_{number}']
            grafik.smena = smena_data 
            grafik.save()
        except Exception as err:
            print(err)
            grafik = Grafik()
            grafik.number = request.POST['start_time']
            grafik.grafik_name = request.POST['grafik_name']
            smena_data = ''
            for number in range(0,int(request.POST['start_time'])):
                if smena_data == '':
                    smena_data += request.POST[f'filter_{number}']
                else:
                    smena_data += ',' + request.POST[f'filter_{number}'] 
            grafik.smena = smena_data
            grafik.save()
        return HttpResponseRedirect('/reports/grafik')
    return render(request, 'skud/views/reports/grafik.html', {'smena': Smena.objects.all(),
                                                            'grafik': Grafik.objects.all()})

def new_grafik(request):
    data = dict()
    smena_name = list(Smena.objects.all().values('smena_name','id'))
    smena_data = list(Smena.objects.all().values_list('smena_name','start_time','end_time','start_break', 'end_break', 'id'))
    grafik = list(Grafik.objects.all().values('id','number', 'grafik_name', 'smena'))
    return JsonResponse({'smena': smena_name,
                        'smena_data': smena_data,
                        'grafik': grafik,
    })

def user_grafik(request):
    if request.method == 'POST':
        data = json.load(request)
        record = data.get('data')
        for user in record['user_list']:
            users = User_list.objects.get(user_id=user)
            users.grafik_id = record['graph_id']
            users.start_time = record['start_time']
            users.end_time = record['end_time']
            users.save()
        
    return render(request, 'skud/views/reports/user_grafik.html',
                    {'department':Department.objects.all(),
                    'grafik': Grafik.objects.all(),
                    'users': User_list.objects.all(),
                    })

def grafik_delete(request, id):
    try:
        device = get_object_or_404(Grafik, id=id).delete()
    except Exception as err:
        print(err)
        messages.error(request, '???? ?????????????? ??????????????') 
    return HttpResponseRedirect('/reports/grafik')

def getUsers_id(request, id):
    data = list(User_list.objects.filter(Q(department__id=id) | Q(department__parent_id=id)).values_list('surname','name', 'user_id'))
    print(data)
    return JsonResponse({'graf':data})






class AllReports():
    def __init__(self, start_report, end_report) -> None:
        self.start_report = start_report
        self.end_report = end_report

    def start(self, select, user):
        if select == '1':
            users_report = []
            for delta in self.start_and_end_report(user):
                if self.employee_schedule(user, delta):
                    users_report.append(self.employee_schedule(user, delta)) 
            return users_report
        elif select == '2':
            users_report = []
            for delta in self.start_and_end_report(user):
                if self.list_of_latecomers(user, delta):
                    users_report.append(self.list_of_latecomers(user, delta)) 
            return users_report
        elif select == '3':
            users_report = []
            for delta in self.start_and_end_report(user):
                if self.list_of_early_care(user, delta):
                    users_report.append(self.list_of_early_care(user, delta))
            return users_report 
        elif select == '4':
            users_report = []
            for delta in self.start_and_end_report(user):
                if self.missing(user, delta):
                    users_report.append(self.missing(user, delta))
            return users_report
        elif select == '6':
            users_report = []
            for delta in self.start_and_end_report(user):
                if self.work_time(user, delta):
                    users_report.append(self.work_time(user, delta))
            return users_report

    def rest_cycle(self, delta, user):
        try:
            start_cycle = (delta - user.start_time).days % user.grafik.number
            return start_cycle
        except Exception as ex:
            print(ex)

    def start_and_end_report(self, user):
        if self.start_report < user.start_time:
            curr = user.start_time
        else:
            curr = self.start_report
        if self.end_report > user.end_time:
            end_date = user.end_time
        else:
            end_date = self.end_report
        if end_date > date.today():
            end_date = date.today()
        while curr <= end_date:
            yield curr
            curr += timedelta(days=1)

    def list_of_latecomers(self, user, delta):
        # ???????????? ??????????????????
            first_time_in = Main_report.objects.filter(Q(user_id=user.id) & Q(data=delta) & Q(in_out_state="????????")).order_by('check_time').first()
            shedule = self.rest_cycle(delta, user)
            smena_id = literal_eval(user.grafik.smena)[int(shedule)] 
            if smena_id != '0': 
                shift = Smena.objects.get(id=smena_id)
                if first_time_in:
                    if first_time_in.check_time > shift.start_time: 
                        first_time_in.times = shift.start_time
                        first_time_in.difference = timedelta(hours=first_time_in.check_time.hour, minutes=first_time_in.check_time.minute, seconds=first_time_in.check_time.second) - timedelta(hours=shift.start_time.hour, minutes=shift.start_time.minute, seconds=shift.start_time.second) 
                        return first_time_in

    def list_of_early_care(self, user, delta):
        # ???????????? ????????
        last_time_in = Main_report.objects.filter(Q(user_id=user.id) & Q(data=delta) & Q(in_out_state="??????????")).order_by('check_time').last()
        shedule = self.rest_cycle(delta, user)
        smena_id = literal_eval(user.grafik.smena)[int(shedule)] 
        if smena_id != '0': 
            shift = Smena.objects.get(id=smena_id)
            if last_time_in:
                if last_time_in.check_time < shift.end_time:
                    last_time_in.times = shift.end_time
                    last_time_in.difference = timedelta(hours=shift.end_time.hour, minutes=shift.end_time.minute, seconds=shift.end_time.second) - timedelta(hours=last_time_in.check_time.hour, minutes=last_time_in.check_time.minute, seconds=last_time_in.check_time.second) 
                    return last_time_in
    
    def missing(self, user, delta):
        # ????????????????????????
        user_missing = Main_report.objects.filter(Q(user_id=user.id) & Q(data=delta)).order_by('check_time')
        shedule = self.rest_cycle(delta, user)
        smena_id = literal_eval(user.grafik.smena)[int(shedule)] 
        if smena_id != '0': 
            if user_missing.exists() != True:
                user.enter_time = delta
                return {'user': user, 'time': delta}
    
    def employee_schedule(self,user, delta):
        # ???????????? ??????????????????????
        smena_id = literal_eval(user.grafik.smena)[int(self.rest_cycle(delta, user))] 
        if smena_id != '0': 
            first_time_in = Main_report.objects.filter(Q(user_id=user.id) & Q(data=delta) & Q(in_out_state="????????")).order_by('check_time').first()
            last_time_in = Main_report.objects.filter(Q(user_id=user.id) & Q(data=delta) & Q(in_out_state="??????????")).order_by('check_time').last()
            shift = Smena.objects.get(id=smena_id)
            if self.list_of_latecomers(user, delta):
                list_of_latecomers = self.list_of_latecomers(user, delta).difference
            else:
                list_of_latecomers = '-'
            if self.list_of_early_care(user, delta):
                list_of_early_care = self.list_of_early_care(user, delta).difference
            else: 
                list_of_early_care = '-'
            if self.missing(user, delta):
                missing = '????'
            else:
                missing = '??????'
            if self.work_time(user, delta):
                total_time = self.work_time(user, delta)
            else:
                total_time = '-'
            users_report = {'user':user, 
                            'delta':delta, 
                            'start_time':shift.start_time, 
                            'end_time':shift.end_time, 
                            'first_time_in':first_time_in,
                            'last_time_in':last_time_in, 
                            'latecomers':list_of_latecomers,
                            'early_care':list_of_early_care,
                            'missing':missing,
                            'total_time': total_time}
            return users_report

    def work_time(self, user, delta):
        first_time_in = Main_report.objects.filter(Q(user_id=user.id) & Q(data=delta) & Q(in_out_state="????????")).order_by('check_time').first()
        last_time_in = Main_report.objects.filter(Q(user_id=user.id) & Q(data=delta) & Q(in_out_state="??????????")).order_by('check_time').last()
        shedule = self.rest_cycle(delta, user)
        smena_id = literal_eval(user.grafik.smena)[int(shedule)] 
        if smena_id != '0': 
            shift = Smena.objects.get(id=smena_id)
            if first_time_in:
                if last_time_in:
                    enter_time = ''
                    exit_time = ''
                    total_time = timedelta(hours=0,minutes=0, seconds=0)
                    print(total_time)
                    for report in Main_report.objects.filter(Q(user_id=user.id) & Q(data=delta)).order_by('check_time'):
                        if report.in_out_state == '????????':
                            if report.check_time > shift.start_time:
                                enter_time = report.check_time
                            else: 
                                enter_time = shift.start_time
                        elif report.in_out_state == '??????????':
                            exit_time = report.check_time
                        if enter_time and exit_time:
                                report_time = timedelta(hours=exit_time.hour, minutes=exit_time.minute, seconds=exit_time.second) - timedelta(hours=enter_time.hour, minutes=enter_time.minute, seconds=enter_time.second)
                                total_time += report_time
                                enter_time = ''
                                exit_time = '' 
                    return {'user': user, 'total_time':total_time, 'delta': delta} 



# -------------------------------------------------------------------------------------------------