# -*- coding: utf-8 -*-
from network.models import Network
import lib.json as json

def meta(deviceDict):
    items = deviceDict['visible'].items() +  deviceDict['hidden'].items()
    items = sorted(items, key=lambda x: int(x[0]))
    
    visItems = deviceDict['visible'].items()
    visItems = sorted(visItems, key=lambda x: int(x[0]))
  
    deviceDict['meta'] = {}
    deviceDict['meta']['last_seq'] = int(items[-1][0])
    deviceDict['meta']['last_device_id'] = int(visItems[-1][1]['id'])
    
    json.encode(deviceDict)
    return deviceDict
    
def updateMeta(test=False, json_print=False, commit=False):
  
    networks = Network.objects.all()
    for net in networks:
        deviceDict = net.device_dict()
        if deviceDict:
            new = meta(deviceDict)
            if test:
                print new['meta']
                continue
            
            new_json = json.encode(new)
            if json_print:
                print new_json
                
            if commit:
                net.devices_json = new_json
                net.save()