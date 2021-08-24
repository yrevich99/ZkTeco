from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from pyzkaccess.exceptions import ZKSDKError
from .models import Device
from pyzkaccess import ZKAccess, ZK200, ZKSDK
from .forms import DeviceForm
from datetime import datetime
# Create your views here.


def user_list(request):
    return render(request, 'skud/base.html')


def device_list(request):
    return render(request, 'skud/views/all_device.html')


def add_device(request):
    if request.method == 'POST':
        try:
            ip = request.POST['device_ip']
            port = request.POST['device_port']
            connstr = f'protocol=TCP,ipaddress={ip},port={port},timeout=4000,passwd='
            with ZKAccess(connstr=connstr) as zk:
                zk.parameters.datetime = datetime.now()
                device_type = zk.parameters.device_model
                device_serial = zk.parameters.serial_number
                
                

            add_device = Device()
            add_device.device_name = request.POST['device_name']
            add_device.device_ip = request.POST['device_ip']
            add_device.device_port = request.POST['device_port']
            add_device.main_door = 'Да'
            add_device.device_add = 'Да'
            # add_device.device_type = device_type
            add_device.serial_number = device_serial

            add_device.save()
            
        except ZKSDKError as err:
            print(err)
            return HttpResponse("Возникла ошибка соединения")
        except Exception as err:
            print(err)
            return HttpResponse("Возникла ошибка")          
        
    return render(request, 'skud/views/add_device.html')


def search_device(request):
    results = []
    device_counts = 0
    
    try:
        found = ZKSDK('plcommpro.dll').search_device('255.255.255.255',4096)
        device_counts = len(found)
        for device_count in range(0, device_counts):
            copy_found = found[device_count-1].split(',')
            results_copys = {}
            results.append(str(device_count+1))
            for founds in copy_found:
                key, value = founds.split('=')
                if key == 'MAC' or key == 'IP' or key == 'SN' or key == 'Device':
                    results_copys[key] = value
            # add_device = Device.objects.get(serial_number = results_copys['MAC'])
            # if add_device:
            #     results_copys['adds'] = 'Да'
            # else:
            #     results_copys['adds'] = 'Нет'
            for value in results_copys.values():
                results.append(value)
            del results_copys  
            print(results)
    except Exception as err:
        print(err)

    return render(request, 'skud/views/search_device.html', {'results': results,
                                                            'device_counts': device_counts,
                                                            })
