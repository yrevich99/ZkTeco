from django.test import TestCase
from django.shortcuts import render, get_object_or_404
from pyzkaccess import ZKAccess, ZK200, ZKSDK, sdk
from pyzkaccess.exceptions import ZKSDKError
# from models import Device
# Create your views here.



found = ZKSDK('plcommpro.dll').search_device('255.255.255.255',4096)
device_counts = len(found)
params = ZKSDK('plcommpro.dll').get_device_param('DeviceID',4096)
print(params)
results = []
print(found)
for device_count in range(0, device_counts):
    copy_found = found[device_counts-1].split(',')
    results_copys = {}
    results.append(str(device_count+1))
    for founds in copy_found:
        key, value = founds.split('=')
        if key == 'MAC' or key == 'IP' or key == 'SN' or key == 'Device':
            results_copys[key] = value
    for value in results_copys.values():
        results.append(value)
    del results_copys
print(results)