from concurrent.futures import thread
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
from .models import Devices, Door_setting, Department, Access_control, User_list, Id_table, Access_id, Status_access, Transactions, Main_report, Door_report, Smena
from pyzkaccess import ZKAccess, ZK200, ZKSDK, device, door
from pyzkaccess.tables import User, UserAuthorize, Transaction
from .forms import AddDeviceForm, DepartmentForm, CreateAccess, CreateUser, CreateSmena
from datetime import datetime
import json
from django.views.generic.list import ListView
from threading import Thread, Lock, current_thread
from time import sleep
from django.core.signals import request_finished
from django.dispatch import receiver
import django.dispatch

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


#Пользователь---------------------------------------------------------------
def user_list(request):
    users = User_list.objects.all()
    pag = paginations(request, users, 10)
    posts = pag[0]
    page = pag[1]
    return render(request, 'skud/views/users_list.html', {'users': users, 'page': page, 'posts': posts})

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

        # id_table.user_id = request.POST['userId']
        # id_table.department_id = request.POST['department']
        # id_table.save()
        return  HttpResponseRedirect('/users_list')

    return render(request, 'skud/views/user_create.html', {
                'departments': Department.objects.all(),
                'access_levels': Access_control.objects.all(),
                'user_id': ids
                })

def user_edit(request, user_id):
    user = User_list.objects.get(user_id=user_id)
    access = Id_table.objects.filter(user_id=user_id)
    # if access.count() > 0:
    #     access = Id_table.objects.get(user_id=user_id)
    #     print(access)
    return render(request, 'skud/views/user_edit.html',{
                'user': user,
                'departments': Department.objects.all(),
                'access_levels': Access_control.objects.all(),
                'user_access': Id_table.objects.filter(user_id=user_id),
                # 'access_door': access,
                })

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
            set_auth = UserAuthorize(pin=id, timezone_id=1, doors= access).with_zk(zk)
            set_auth.save()
            # if record == False:
            #     return True
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
            # elif record == False:
            #     print('set - ',err)
            #     return False

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
            set_auth = UserAuthorize(pin=id, timezone_id=1, doors= access).with_zk(zk)
            set_auth.delete()
            # if record == False:
            #     return True
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
            #     return False

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
    return  HttpResponseRedirect('/users_list')



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
    
def door_edit(request, id):
    data = dict()
    if request.method == 'POST':
        door = Door_setting.objects.get(id=id)
        door.name_door = request.POST['name_door']
        door.driver_time = request.POST['driver_time']
        door.detector_time = request.POST['detector_time']
        door.inter_time = request.POST['inter_time']
        door.sensor_type = request.POST['sensor_type']
        door.save()
        print(request.POST)
        
    context = {'door': Door_setting.objects.get(id=id)}
    data['html_form'] = render_to_string('skud/views/door_edit.html',
    context,
    request=request)
    return JsonResponse(data)
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

                live = LiveStream(ip=ip)
                live.door4todoor2({'Door4ToDoor2':request.POST['todoor']})


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
            live = LiveStream(ip=request.POST['device_ip'])
            live.door4todoor2({'Door4ToDoor2':request.POST['todoor']})

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
    data = dict()
    try:
        device = Devices.objects.get(id=id)
        connstr = f'protocol=TCP,ipaddress={device.device_ip},port={device.device_port},timeout=4000,passwd='
        
        with ZKAccess(connstr=connstr) as zk:
            zk.parameters.datetime = datetime.now()
            message_time = 'Время установлено'
        data['message'] = message_time
    except Exception as err:
        print(err)
        message_time = 'Не удалось установить время'
        data['message'] = message_time
        
    return JsonResponse(data)
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

#Доступ-----------------------------------------------------------------------------------
def access_control(request):
    return render(request, 'skud/views/access_control.html', {'access_control':Access_control.objects.all()})

def access_delete(request,access_name):
    try:
        access = get_object_or_404(Access_control, access_name=access_name)
        access_id = Access_id.objects.filter(access_id=access.id)
        print(access_id)
        access_id.delete()
        access.delete()

        return  HttpResponseRedirect('/access_control')
    except Exception as err:
        return  HttpResponse('Невозможно удалить так как у пользователя есть данный доступ')

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
            '1': 'Отпечаток',
            '3': 'Пароль',
            '4': 'Карта',
            '6': 'Карта или отпечаток',
            '10': 'Карта и отпечаток',
            '11': 'Карта и пароль',
            '200': 'Другое'
        }
        if num in verify:
            return verify[num]
        else:
            return 'Другое'
        
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
            '0': 'Вход',
            '1': 'Выход',
            '2': 'Неизвестно'
        }
        if state in status:
            return status[state]
        else:
            return 'Unknown'

    def event_type(self, event):
        event_list = {
            '0': 'Открытие картой',
            '1': 'Нормальное открытие во временной зоне',
            '2': 'Ожидание следующего пользователя(Карта)',
            '3': 'Открыто групповым доступом(Карта)',
            '4': 'Открыто аварийным паролем ',
            '5': 'Открыто в Обычном часовом поясе',
            '6': 'Инициированное событие Связи',
            '7': 'Отмена сигнальной тревоги',
            '8': 'Дистанционное Открытие',
            '9': 'Дистанционное Закрытие',
            '10': 'Отключено Внутридневное событие',
            '11': 'Включено Внутридневное событие',
            '12': 'Открыт AUX вывод',
            '13': 'Закрыт AUX вывод',
            '14': 'Открыто отпечатком',
            '15': 'Открыто групповым доступом(Отпечаток)',
            '16': 'Открыто отпечатком',
            '17': 'Открыто картой + отпечаток',
            '18': 'Ожидание следующего пользователя(Отпечатоком пальца)',
            '19': 'Ожидание следующего пользователя(Карта + Отпечаток Пальца)',
            '20': 'Слишком Короткий Интервал Между Проходами',
            '21': 'Часовой пояс Двери Неактивен',
            '22': 'Незаконный часовой пояс',
            '23': 'Доступ запрещен',
            '24': 'Защита от обратного прохода',
            '25': 'Блокировка',
            '26': 'Аутентификация с использованием Нескольких Карт',
            '27': 'Незарегистрированная Карта',
            '28': 'Время задержки истекло после открытия',
            '29': 'Срок действия карты истек',
            '30': 'Ошибка пароля',
            '31': 'Слишком Короткий Интервал Нажатия Отпечатка Пальца',
            '32': 'Аутентификация с помощью нескольких карт (Отпечаток пальца)',
            '33': 'Срок действия отпечатка пальца истек',
            '34': 'Незарегистрированный отпечаток пальца',
            '35': 'Часовой пояс Двери Неактивен (Отпечаток пальца)',
            '36': 'Часовой пояс Двери Неактивен (Кнопка Выхода)',
            '37': 'Не удалось закрыть дверь',
            '101': 'Открыт Принудительным Паролем ',
            '102': 'Дверь Открылась Случайно',
            '103': 'Принужденное Открытие Отпечатком Пальца',
            '200': 'Дверь Открылась Правильно',
            '201': 'Дверь Закрыта Правильно',
            '202': 'Дверь Открыта Кнопкой ',
            '203': 'Открытие груповым доступом',
            '204': 'Нормальное открытие',
            '205': 'Удаленное открытие',
            '206': 'Запуск устройства',
            '220': 'Вспомогательный Вход Отключен',
            '221': 'Вспомогательный Вход Закорочен',
            '255': 'Статус двери и Статус сигнализации',
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
            user['name'] = 'Незарегистрированный пользователь'
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
                            if Devices.objects.get(device_ip=self.ip).main_door == 'Да':
                                report = Main_report()
                                report.user_id = user.id
                                report.user_pin = int(tables[i].raw_data['Pin'])
                                report.data = datatime[0]
                                report.check_time = datatime[1]
                                report.in_out_state = self.in_out_state(tables[i].raw_data['InOutState'])
                                report.door_name = self.door_name(tables[i].raw_data['DoorID'])
                                report.save()
                                tables[i].delete()
                            elif Devices.objects.get(device_ip=self.ip).main_door == 'Нет':
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
        # tables = [{'time': '2022-02-05 16:37:42', 'pin': '1', 'surname': '', 'name': 'Чужой', 'card': '3545531', 'door': '4', 'event': '0', 'entry_exit': '0', 'verify': '6'},
        #         {'time': '2022-02-05 16:37:42', 'pin': '0', 'surname': '', 'name': 'Чужой', 'card': '0', 'door': '4', 'event': '27', 'entry_exit': '0', 'verify': '6'},
        #         {'time': '2022-02-05 16:37:43', 'pin': '1', 'surname': '', 'name': 'Чужой', 'card': '3545531', 'door': '4', 'event': '0', 'entry_exit': '0', 'verify': '6'}, 
        #         {'time': '2022-02-05 16:37:44', 'pin': '0', 'surname': '', 'name': 'Чужой', 'card': '0', 'door': '4', 'event': '27', 'entry_exit': '0', 'verify': '6'},
        #         {'time': '2022-02-05 16:37:45', 'pin': '1', 'surname': '', 'name': 'Чужой', 'card': '3545531', 'door': '4', 'event': '0', 'entry_exit': '0', 'verify': '6'}]
        print(self.ip)
        return tables
        

global live
live = {}

def monitoring(request):
    return render(request, 'skud/views/monitoring.html', {'device': Devices.objects.all()})


def monitoring_js(request, ip):
    data = dict()
    live['monitoring'] = LiveStream(ip)
    data['real'] = live['monitoring'].live_mode()
    context = {'dates': data['real']}
    return JsonResponse(data)
# ---------------------------------------------------------------------------------------


# Отчет ------------------------------------------------------------------------------------------
def reports_list(request):
    if request.method == 'POST':
        if request.POST['filter'] == '1':
            return render(request, 'skud/views/reports/all_reports.html', 
            {'main_report': Main_report.objects.filter(data__range=[request.POST['start_time'],request.POST['end_time']]), 
            'time_now': datetime.now().strftime ("%Y-%m-%d")})
    return render(request, 'skud/views/reports/report.html', {'time_now': datetime.now().strftime ("%Y-%m-%d")})

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
    return render(request, 'skud/views/reports/grafik.html', {'smena': Smena.objects.all()})

def new_grafik(request):
    # data = dict()
    smena_name = list(Smena.objects.all().values('smena_name','id'))
    smena_data = list(Smena.objects.all().values_list('smena_name','start_time','end_time','start_break', 'end_break', 'id'))
    return JsonResponse({'smena': smena_name,
                        'smena_data': smena_data
    })
# -------------------------------------------------------------------------------------------------
