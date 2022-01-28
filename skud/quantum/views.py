from concurrent.futures import thread
import threading
from typing import Dict
from django import http
from django.forms.fields import MultiValueField
from django.template.loader import render_to_string
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from pyzkaccess.exceptions import ZKSDKError
from .models import Devices, Door_setting, Department, Access_control, User_list, Id_table, Access_id, Status_access
from pyzkaccess import ZKAccess, ZK200, ZKSDK, device, door
from pyzkaccess.tables import User, UserAuthorize, Transaction
from .forms import AddDeviceForm, DepartmentForm, CreateAccess, CreateUser
from datetime import datetime
import json
from django.views.generic.list import ListView
from threading import Thread, Lock, current_thread
from time import sleep
# Create your views here.

#Пользователь---------------------------------------------------------------
def user_list(request):
    return render(request, 'skud/views/users_list.html', {'users': User_list.objects.all(),'departments': Department.objects.all()})

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
        id_table = Id_table()
        new_user.user_id = request.POST['userId']
        new_user.surname = request.POST['surname']
        new_user.name = request.POST['name']
        new_user.department_id = request.POST['department']
        new_user.card_number = request.POST['card_number']

        try:
            access_list =  request.POST.getlist('access')
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

        id_table.user_id = request.POST['userId']
        id_table.department_id = request.POST['department']
        id_table.save()
        return  HttpResponseRedirect('/users_list')

    return render(request, 'skud/views/user_create.html', {
                'departments': Department.objects.all(),
                'access_levels': Access_control.objects.all(),
                'user_id': ids
                })

def set_access_user(id: str,card,lock):
    ip_and_access = lock.split(';')
    for item in ip_and_access:
        key_and_value = item.split(',')
        ip = key_and_value[0]
        access = int(key_and_value[1])
        try:
            zk = ZKAccess(f'protocol=TCP,ipaddress={ip},port=4370,timeout=4000,passwd=')
            set_user = User(card=card, pin=id).with_zk(zk)
            set_auth = UserAuthorize(pin=id, timezone_id=1, doors= access).with_zk(zk)
            set_user.save()
            set_auth.save()
        except Exception as err:
            status = Status_access()
            status.user_id = id
            status.user_card = card
            status.access_lock = access
            status.device_ip = ip
            status.status_access = True
            status.save()

def del_access_user(id: str,card,lock):
    ip_and_access = lock.split(';')
    for item in ip_and_access:
        key_and_value = item.split(',')
        ip = key_and_value[0]
        access = int(key_and_value[1])
        try:
            zk = ZKAccess(f'protocol=TCP,ipaddress={ip},port=4370,timeout=4000,passwd=')
            set_auth = UserAuthorize(pin=id, timezone_id=1, doors= access).with_zk(zk)
            set_auth.delete()
        except Exception as err:
            status = Status_access()
            status.user_id = id
            status.user_card = card
            status.access_lock = access
            status.device_ip = ip
            status.status_access = False
            status.save()



def user_delete(request,user_id):
    try:
        user_list = get_object_or_404(User_list, user_id=user_id)
        if user_list.access_id != '':
            access_list = user_list.access_id.split(';')
            for i in access_list:
                if Access_control.objects.get(access_name=i):
                    lock_list = Access_control.objects.get(access_name=i).lock_control
                    del_user_access = del_access_user(id=user_list.user_id, card=user_list.card_number, lock=lock_list)
                else:
                    print('Error')
        user_list.delete()
        user_table = Id_table.objects.filter(user_id=user_id).delete()
        return  HttpResponseRedirect('/users_list')
    except Exception as err:
        print(err)
        return  HttpResponseRedirect('/users_list')
#-------------------------------------------------------------------------------------

#Двери-------------------------------------------------------------------------------------
def door_setting_list(request):
    return render(request, 'skud/views/door_setting.html', {'doors': Door_setting.objects.all()})

def door_setting_get(ip,port,parametrs):
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
#-------------------------------------------------------------------------------------------------------

#Устройства----------------------------------------------------------------------------
def search_list(request):
    return render(request, 'skud/views/search_device.html')

def search_device_list(request):
    search = search_devices()
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
                dev = ip_search(ip)

                # Добавление устройства ---------------------------------------------------------
                add_device = Devices()
                add_device.device_name = request.POST['device_name']
                add_device.device_ip = request.POST['device_ip']
                add_device.device_port = request.POST['device_port']
                add_device.device_add = 'Да'
                add_device.device_mac = dev['MAC']
                add_device.device_type = dev['Device']
                add_device.serial_number = dev['SN']
                if request.POST.get('main_door'):
                    add_device.main_door = 'Да'
                else:
                    add_device.main_door = 'Нет'
                add_device.save()

                # Добавление двери--------------------------------------------------------
                lock_count = door_setting_get(ip,port,"LockCount")
                lock_count = int(lock_count["LockCount"])
                
                for counts in range(1,(lock_count+1)):
                    parameters = f'Door{counts}Drivertime,Door{counts}Detectortime,Door{counts}Intertime,Door{counts}SensorType'
                    door_setting = Door_setting()
                    get_param = door_setting_get(ip,port,parameters)
                    door_setting.door_number = counts
                    door_setting.device_ip = request.POST['device_ip']
                    door_setting.name_door = (request.POST['device_name'] + '-' + str(counts))
                    door_setting.device_name = request.POST['device_name']
                    door_setting.driver_time = int(get_param[f'Door{counts}Drivertime'])
                    door_setting.detector_time = int(get_param[f'Door{counts}Detectortime'])
                    door_setting.inter_time = int(get_param[f'Door{counts}Intertime'])
                    if (int(get_param[f'Door{counts}SensorType']) == 0):
                        door_setting.sensor_type = 'Не указано'
                    elif (int(get_param[f'Door{counts}SensorType']) == 1):
                        door_setting.sensor_type = 'Нормально - открытая'
                    elif (int(get_param[f'Door{counts}SensorType']) == 2):
                        door_setting.sensor_type = 'Нормально - закрытая'
                    door_setting.save()
                # ------------------------------------------------------------------------------

            return HttpResponseRedirect('/device_list')
        except ZKSDKError as err:
            print(err)
            return HttpResponse("Ошибка соединения")
        except Exception as err:
            print(err)
            return HttpResponse("Возникла ошибка")
    return render(request, 'skud/views/add_device.html')

def edit_device(request, id):
    if request.method == 'POST':
        try:
            device = Devices.objects.get(id=id)
            door = Door_setting.objects.filter(device_name=device.device_name)
            
            for counts in range(0, len(door)):
                door[counts].device_name = request.POST['device_name']
                door[counts].save()
            device.device_name = request.POST['device_name']
            device.save()
            
        except Exception as err:
            print(err)
            return HttpResponse("Девайс не найден")
        
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
        return HttpResponse('Error')
    return HttpResponseRedirect('/device_list')

def search_devices():
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
                results_copys['adds'] = 'Да'
            else:
                results_copys['adds'] = 'Нет'

            results.append(results_copys)
            del results_copys  
        return [results,device_counts]
    except Exception as err:
        print(err)
        return 'error'

def ip_search(ip):
    found = ZKSDK('plcommpro.dll').search_device(ip,4096)
    device_counts = len(found)
    copy_found = found[0].split(',')
    results_copys = {}

    for founds in copy_found:
        key, value = founds.split('=')

        if key == 'MAC' or key == 'IP' or key == 'SN' or key == 'Device':
            results_copys[key] = value
    return results_copys

def current_time(request, id):
    try:
        device = Devices.objects.get(id=id)
        connstr = f'protocol=TCP,ipaddress={device.device_ip},port={device.device_port},timeout=4000,passwd='
        
        with ZKAccess(connstr=connstr) as zk:
            zk.parameters.datetime = datetime.now()
            print('Успешно')
            message_time = 'Время установлено'
        
    except Exception as err:
        print(err)
        message_time = 'Не удалось установить время'
        # return HttpResponse('Error')
    
    # return render_to_response('skud/views/all_device.html', message='Время установлено успешно')
    return HttpResponseRedirect('/device_list')
#---------------------------------------------------------------------

#Отдел-----------------------------------------------------------
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
    
    context = {'form': form}
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

class DepartmentView(ListView):
    model = Department
    template_name = 'department_form.html'
    context_object_name = 'deps'
#--------------------------------------------------------------------------------

#Доступ-----------------------------------------------------------------------------------
def access_control(request):
    return render(request, 'skud/views/access_control.html', {'access_control':Access_control.objects.all()})

def access_delete(request,access_name):
    access = get_object_or_404(Access_control, access_name=access_name).delete()
    return  HttpResponseRedirect('/access_control')

def access_create(request):
    form = CreateAccess(request.POST)
    
    if request.method == 'POST':
        try:
            if form.is_valid():
                lock_list = request.POST.getlist('lock_control')
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


#Мониторинг------------------------------------------------------------------------------
class LiveStream():
    def __init__(self) -> None:
        self.lock = Lock()
        self.status = None
        self.ip = None
        self.position = 'None'

    def status_position(self):
        return self.position
        
    def transaction(self):
        conn = f'protocol=TCP,ipaddress={self.ip},port=4370,timeout=4000,passwd='
        zk = ZKAccess(conn)
        table = []
        tables = zk.table('Transaction')
        if tables.count() > 0:
            for i in range(tables.count()):
                print(i,'---',tables[i])
                table.append(tables[i])
            # print(table)
        else:
            return False
        

    def live_mode(self):
        conn = f'protocol=TCP,ipaddress={self.ip},port=4370,timeout=4000,passwd='
        table = {}
        zk = ZKSDK('plcommpro.dll')
        zk.connect(conn)
        rt_logs = zk.get_rt_log(256)
        print(rt_logs)
        for rt_log in rt_logs:
            item = rt_log.split(',')
            if item[4] == '255':
                continue
            else:
                table['time'] = item[0]
                table['pin'] = item[1]
                table['card'] = item[2]
                table['door'] = item[3]
                table['event'] = item[4]
                table['entry/exit'] = item[5]
                table['verify'] = item[6]
            print(table)
        zk.disconnect()
        

    def live_stream(self):
        while True:
            self.lock.acquire()
            if self.status is False:
                break
            self.live_mode()
            self.lock.release()
            sleep(3)
    
    def start(self):
        self.status = True
        self.th = Thread(name='live',target=self.live_stream)
        self.th.start()

    def stop(self):
        self.lock.acquire()
        self.status = False
        self.lock.release()
        
global live
live = {}
# live = LiveStream()

def monitoring(request):
    if request.method == "POST":
        if 'monitoring' in live.keys():
            status = request.POST['status']
            if status == 'True':
                live['monitoring'].ip = request.POST['device_ip']
                live['monitoring'].start()
            elif status == 'False':
                live['monitoring'].stop()
        else:
            live['monitoring'] = LiveStream()
            status = request.POST['status']
            if status == 'True':
                live['monitoring'].ip = request.POST['device_ip']
                live['monitoring'].start()
            elif status == 'False':
                live['monitoring'].stop()

            


    return render(request, 'skud/views/monitoring.html', {'device': Devices.objects.all()})
# ---------------------------------------------------------------------------------------

