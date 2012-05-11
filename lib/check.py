# -*- coding: utf-8 -*-
from network.models import Network, SPIC

amountHidden={
    1: 0,
    2: 1,
    3: 1,
    4: 5,
    5: 1,
    6: 0,
}
networkList = Network.objects.all()


errMsg = {
  'posNeuron':          'missed positions in neurons',
  'lastDeviceId':       'wrong last device ID in devices',
  'lastSeq':            'wrong last sequence in devices',
  'hiddenDevices':      'missed hidden devices in network',
  'emptyDevicesJson':   'devices json is not empty',
  }
  
cleanMsg = {
  'posNeuron':          'all positions in neurons found.',
  'lastDeviceId':       'all last device ID in devices are correct.',
  'lastSeq':            'all last sequence in devices are correct.',
  'hiddenDevices':      'all hidden devices in network found.',
  'emptyDevicesJson':   'devices json is empty',
  }  

errorDict = {}
posNeuronsList, lastSeqList, lastDeviceIdList, hiddenDevicesList = [],[],[],[]
for network in networkList:
    deviceDict = network.device_dict()
    
    if network.devices_json:
        if not deviceDict:
            errorNetwork['emptyDevicesJson'] = network.devices_json
    
    if deviceDict:
        errorNetwork = {}
        # Check positions of neurons
        neuronList = network.device_list(modeltype='neuron')
        missedList = []
        for neuron in neuronList:
            if not 'position' in neuron:
                missedList.append(str(neuron['id']))
        if missedList:
            errorNetwork['posNeuron'] = 'missed positions in device[id]: '+ ','.join(missedList)
            
        # Check the last device id value in meta
        itemsVis = deviceDict['visible'].items()
        itemsVis = sorted(itemsVis, key=lambda x: int(x[0]))
        lastDeviceIdVal = deviceDict['meta']['last_device_id']
        if lastDeviceIdVal != int(itemsVis[-1][1]['id']):
            errorNetwork['lastDeviceId'] = 'has:%s, should:%s' %(str(lastDeviceIdVal), str(itemsVis[-1][1]['id']))
            
        # Check the last sequence value in meta
        itemsAll = itemsVis + deviceDict['hidden'].items()
        itemsAll = sorted(itemsAll, key=lambda x: int(x[0]))
        lastSeqVal = deviceDict['meta']['last_seq']
        if lastSeqVal != int(itemsAll[-1][0]):
            errorNetwork['lastSeq'] = 'has:%s, should:%s' %(str(lastSeqVal), str(itemsAll[-1][0]))
        
        # Check correct amount of hidden devices
        hiddenList = network.device_list('hidden')
        spic_id = network.SPIC.pk
        hiddenVal = amountHidden[spic_id]
        if len(hiddenList) != hiddenVal:
            errorNetwork['hiddenDevices'] = 'SPIC:%s, has:%s, should:%s' %(spic_id, len(hiddenList), hiddenVal)
            
    if errorNetwork:
        errorDict[network.pk] = errorNetwork

print 'All networks are checked and',
if errorDict:
    print 'some networks are invalid.'
    amountHiddenStr = ["%s -> %s" %(i, j) for i,j in amountHidden.items()]
    print 'List if hidden devices for each SPIC: '+', '.join(amountHiddenStr)
    for pk, errors in errorDict.items():
        print 'Error in Network: Id=%s' %pk
        for key, msg in errors.items():
            print ' - '+ errMsg[key] +': '+ msg
else:
    print 'they are clean.'
    for msg in cleanMsg.values():
        print ' - '+ msg
    