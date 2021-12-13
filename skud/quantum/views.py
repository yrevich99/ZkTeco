from typing import Dict
from django import http
from django.template.loader import render_to_string
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from pyzkaccess.exceptions import ZKSDKError
from .models import Devices, Door_setting, Department
from pyzkaccess import ZKAccess, ZK200, ZKSDK, device, door
from .forms import AddDeviceForm, DepartmentForm
from datetime import datetime
# Create your views here.

def user_list(request):
    return render(request, 'skud/views/users_list.html')


def user_create(request):
    return render(request, 'skud/views/user_create.html')

def device_list(request):
    devices = Devices.objects.all()
    counts_device = 1
    return render(request, 'skud/views/all_device.html', {'devices': devices, 'counts_device':counts_device})

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

def door_setting_list(request):
    return render(request, 'skud/views/door_setting.html', {'doors': Door_setting.objects.all()})


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
                # print(request.POST['main_door'])
                # if (request.POST["main_door"] == 'true'):
                #     add_device.main_door = 'Да'
                # else:
                #     add_device.main_door = 'Нет'
                add_device.save()

                # Добавление двери--------------------------------------------------------
                lock_count = door_setting_get(ip,port,"LockCount")
                lock_count = int(lock_count["LockCount"])
                
                for counts in range(1,(lock_count+1)):
                    parameters = f'Door{counts}Drivertime,Door{counts}Detectortime,Door{counts}Intertime,Door{counts}SensorType'
                    door_setting = Door_setting()
                    get_param = door_setting_get(ip,port,parameters)
                    door_setting.door_number = counts
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
        
    
def access_control(request):
    pass

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
    
# Отдел -----------------------------------------------------------
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
# --------------------------------------------------------------------------------

def access_control(request):
    return render(request, 'skud/views/access_control.html')