# -*- coding: utf-8 -*-
from reversion import revision

import numpy as np
from network.network_settings import PARAMS_ORDER

params_order = {}
for key, val in PARAMS_ORDER.items():
    params_order[key] = val[0] + val[1]

#@revision.create_on_success
#def revision_create(obj, result=False, **kwargs):
    #""" Create a revision for network object. """
    #obj.save()
    #if result:
        #revision.add_meta(Result, **kwargs)
        
def values_extend(values, unique=False, toString=False):
    """ Extend targets/sources e.g. if target is '1-3, 5', it converts into '1,2,3,5'. """
    
    value_list = values.split(',')
    extended_list = []
    for value in value_list:
        if '-' in value:
            start, end = value.split('-')
            
            assert int(start) < int(end)
            value = [i for i in range(int(start), int(end)+1)]
            extended_list.extend(value)
        else:
            extended_list.append(int(value))
            
    # Make each target/source value unique and sorted
    if unique:
        extended_list = list(set(extended_list))
    extended_list = sorted(extended_list, key=lambda x: int(x))
        
    # Convert each value into string
    if toString:
        extended_list = map(lambda x: str(x), extended_list)
        
    return extended_list

def id_escape(id_filterbank, seq=None):
    """ Return user visible id from true id. """
    if id_filterbank.any():
        seqs = np.array(id_filterbank[:,0], dtype=int)
        ids = np.array(id_filterbank[:,1], dtype=int)

        if int(seq) in seqs: 
            return ids[seqs.tolist().index(int(seq))]
        
    return -1
    
def id_identify(id_filterbank, id=None):
    """ Return true id from user visible id. """
    if id_filterbank.any():
        seqs = np.array(id_filterbank[:,0], dtype=int)
        ids = np.array(id_filterbank[:,1], dtype=int)
        
        if id == -1:
            return seqs[ids == -1]
        
        if int(id) in ids: 
            return seqs[ids.tolist().index(int(id))]
        
    return -1
    
def dict_to_JSON(valDict):
    params_order = PARAMS_ORDER[valDict['model']][0] + PARAMS_ORDER[valDict['model']][1]
    valList = []
    
    for keyJSON in params_order:
        if keyJSON in valDict:
            if valDict[keyJSON]:
                valList.append('"%s":"%s"' %(keyJSON, valDict[keyJSON]))
                continue
        valList.append('"%s":""' %keyJSON)
        
    return '{' + ', '.join(valList) + '}'
    
def csv_to_dict(csv):
    csvList = csv.split('\r\n')
    devList = []
    for device in csvList:
        statusList = device.split(';')
        statusList = [status.lstrip() for status in statusList]
        statusList[1] = int(statusList[1])
        if statusList[0] in params_order:
            params = params_order[statusList[0]]
            devList.append(dict(zip(params,statusList)))
    return devList
    
def delete_devices(deviceList, device_ids):
    del_ids = device_ids.copy()
    
    # check if inputs/outputs also should be deleted.
    for device in deviceList:
        if device['type'] == 'input' or device['type'] == 'output':
            if 'sources' in device:        
                key = 'sources'
            else:
                key = 'targets'
                
            if device.get(key):
                neuronList = np.array(device[key].split(','), dtype=int)
                delete = True
                for neuron in neuronList:
                    if not neuron in device_ids:
                        delete = False
                        
                if delete:
                    del_ids = np.append(del_ids, device['id'])
    
    new_deviceList = []
    for device in deviceList:
        if not device['id'] in del_ids:

            # delete target/source
            new_conns = {}
            if 'targets' in device or 'sources' in device:
                if 'targets' in device:
                    key = 'targets'
                elif 'sources' in device:        
                    key = 'sources'
                    
                if device.get(key):
                    value_list = device[key].split(',')
                    value_array = np.array([item for item in enumerate(value_list) if int(item[1]) not in del_ids], dtype=int)
                    
                    if value_array.any():
                        # delete weight and delay
                        if device.get('weight'):
                            weight_list = device['weight'].split(',')
                            if len(weight_list) > 1 and len(value_array) > 1:
                                weight_list = [str(item[1]) for item in enumerate(weight_list) if item[0] in value_array[:,0]]
                            if not weight_list == ['']:
                                device['weight'] = ','.join(weight_list)
                            
                        if device.get('delay'):
                            delay_list = device['delay'].split(',')
                            if len(delay_list) > 1 and len(value_array) > 1:
                                delay_list = [str(item[1]) for item in enumerate(delay_list) if item[0] in value_array[:,0]]
                            if not delay_list == ['']:
                                device['delay'] = ','.join(delay_list)
                    
            # append all status to new list
            new_deviceList.append(device)
            
    return new_deviceList