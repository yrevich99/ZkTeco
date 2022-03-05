from sqlite3 import Time
from time import sleep
from django.test import TestCase
from django.shortcuts import render, get_object_or_404
from pyzkaccess import ZKAccess, ZK200, ZKSDK, sdk
from pyzkaccess.exceptions import ZKSDKError
from pyzkaccess.tables import User, UserAuthorize
from ctypes import *
from threading import *
import itertools
from datetime import datetime
# from models import Device
# Create your views here.
# from .models import Department
# rock = Department.objects.create(name="Rock")
# blues = Department.objects.create(name="Blues")
# Department.objects.create(name="Hard Rock", parent=rock)
# Department.objects.create(name="Pop Rock", parent=rock)
# def timers():
    

# con = ZKAccess(zk)
# my_users = User(card='3545531', pin='123').with_zk(con)
# my_user = UserAuthorize(pin='123', timezone_id=1, doors= 15).with_zk(con)
# my_users.save()
# my_user.save()
# get_rt

zk = 'protocol=TCP,ipaddress=192.168.1.203,port=4370,timeout=4000,passwd='
conn = ZKSDK('plcommpro.dll')

conn.connect(zk)
tables = conn.get_rt_log(256)
print(tables)


print((710436534/60)%60)

def time_dex(time):
    time = int(time)
    Second = time  %  60
    Minute = int(( time / 60 ) % 60)
    Hour =  int(( time / 3600 ) % 24)
    Day = int(( time / 86400 )  %  31 + 1)
    Month= int(( time / 2678400 ) % 12 + 1)
    Year = int((time / 32140800 ) + 2000)


    datetime_object = datetime.strptime(f'{Year}-{Month}-{Day} {Hour}:{Minute}:{Second}', "%Y-%m-%d %H:%M:%S")
    return datetime_object

conn = f'protocol=TCP,ipaddress=192.168.1.203,port=4370,timeout=4000,passwd='
zk = ZKAccess(conn)
tables = []
transaction = zk.table('Transaction')
if transaction.count() > 0:
    for i in range(transaction.count()):
        
        # print(i,'---',transaction[i])
        tables.append(transaction[i])
        

        print(transaction[i].raw_data['Cardno'])
    print(transaction[0].raw_data)

    # print(tables)


# if tabe.count() > 0:
#     print(tabe[0])
# print(tables[0])
# x = next(itertools.islice(x, p))
# print(x)
# for tabes in tables:
#     print(tabes)

# t = Timer(5, timers)
# t.start()

# zk = 'protocol=TCP,ipaddress=192.168.1.203,port=4370,timeout=4000,passwd='
# con = ZKAccess(zk)
# txns = con.table('Transaction')
# if txns.count() > 0:
#     print('The first transaction:', txns[0])
# else:
#     print('Transaction table is empty!')
# print(txns)
# table = conn.set_device_data('userauthorize')
# table.send(None)
# rec = User(card='123456', pin='123')
# print(rec.dict)
# records = {'Pin':'19999','AuthorizeTimezoneId':'1', 'AuthorizeDoorId':'7'}

# table.send(records)
# try:
#     table.send(None)
# except StopIteration:
#     pass
# conn.disconnect()




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
# par = "protocol=TCP,ipaddress=192.168.1.202,port=4370,timeout=4000,passwd="
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
# cons = 1
# its = ["DeviceID","Door1SensorType","~SerialNumber","IPAddress","Door1Drivertime","Door1Intertime","Door1Detectortime","ReaderCount"]
# its = ["ReaderCount"]
# itt = f'Door{cons}SensorType,Door{cons}Drivertime,Door{cons}Detectortime'
# itt = itt.split(',')
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

# connects = ZKSDK()
# connects.connect(par)

# gcet_dev = connects.get_device_param(its,2048)
# print(gcet_dev)
# connects.disconnect()

# gcet_dev = int(gcet_dev['ReaderCount'])
# for con in range(1,(gcet_dev+1)):
#     print(con)

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


# dicts = {'Device': 3, 'Девайс 2': 1}
# strings = ""

# for key, value in dicts.items():
#     if strings == '':
#         strings = f'{key}.{value}'
#     else:
#         strings += f';{key}.{value}'
# print(strings)