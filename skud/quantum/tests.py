from django.test import TestCase
from django.shortcuts import render, get_object_or_404
from pyzkaccess import ZKAccess, ZK200, ZKSDK, sdk
from pyzkaccess.exceptions import ZKSDKError
from ctypes import *
# from models import Device
# Create your views here.



# found = ZKSDK('plcommpro.dll').search_device('255.255.255.255',4096)
# print(found)
# device_counts = len(found)
# results = []
# print(found)
# for device_count in range(0, device_counts):
#     copy_found = found[device_counts-1].split(',')
#     results_copys = {}
#     results.append(str(device_count+1))
#     for founds in copy_found:
#         key, value = founds.split('=')
#         if key == 'MAC' or key == 'IP' or key == 'SN' or key == 'Device':
#             results_copys[key] = value
#     for value in results_copys.values():
#         results.append(value)
#     del results_copys
# print(results)


# result = {}
par = "protocol=TCP,ipaddress=192.168.1.202,port=4370,timeout=4000,passwd="
# params = par.encode()
# commpro = windll.LoadLibrary("plcommpro.dll")	
# constr = create_string_buffer(params)

# hcommpro = commpro.Connect(constr)	
# print(hcommpro)
# buffer = create_string_buffer(2048)
# it = ("DeviceID,Door1SensorType,Door1Drivertime,Door1Intertime,Door1Detectortime")
# items = it.encode()
# p_items = create_string_buffer(items)
# ret=commpro.GetDeviceParam(hcommpro, buffer, 256, p_items)
# print(buffer)
# for pair in buffer.value.decode().split(','):
#     key,val = pair.split('=')
#     result[key] = val

# print(result)
cons = 1
its1 = ["DeviceID","Door1SensorType","~SerialNumber","IPAddress","Door1Drivertime","Door1Intertime","Door1Detectortime","ReaderCount"]
its = ["ReaderCount"]
itt = f'Door{cons}SensorType,Door{cons}Drivertime,Door{cons}Detectortime'
itt = itt.split(',')
# print(itt)
# parameters_copy = list(its)
# while parameters_copy:
#     query_params = parameters_copy[:30]
#     query = ','.join(query_params).encode()
#     del parameters_copy[:30]

# ret=commpro.GetDeviceParam(hcommpro, buffer, 256, query)
# for pair in buffer.value.decode().split(','):
#             print(pair)
#             key, val = pair.split('=')
#             result[key] = val

# print(result)

connects = ZKSDK()
connects.connect(par)

gcet_dev = connects.get_device_param(its,2048)
print(gcet_dev)
connects.disconnect()

gcet_dev = int(gcet_dev['ReaderCount'])
for con in range(1,(gcet_dev+1)):
    print(con)

# print(gcet_dev)









# par = "protocol=TCP,ipaddress=192.168.1.202,port=4370,timeout=4000,passwd="
# params = par.encode()
# commpro = windll.LoadLibrary("plcommpro.dll")	
# # constr = create_string_buffer(params)

# hcommpro = commpro.Connect(params)	
# buffer = create_string_buffer(2048)
# result = {}
# its = ["DeviceID","Door1SensorType","Door1Drivertime","Door1Intertime","Door1Detectortime"]

# parameters_copy = list(its)
# while parameters_copy:
#     query_params = parameters_copy[:30]
#     query = ','.join(query_params).encode()
#     del parameters_copy[:30]

# ret=commpro.GetDeviceParam(hcommpro, buffer, 256, query)
# items = parameters_copy.encode()
# p_items = create_string_buffer(parameters_copy)

# for pair in buffer.value.decode().split(','):
#             # print(pair)
#             key, val = pair.split('=')
#             result[key] = val

# print(result)
