# -*- coding: utf-8 -*-

from network.models import Network

def positions(id=None, user_id=None):

    if id:
        networkList = Network.objects.filter(pk=id)
    elif user_id:
        networkList = Network.objects.filter(user_id=user_id)
    else:
        networkList = Network.objects.all()

    missedList = []
    for network in networkList:
        for neuron in network.device_list(modeltype='neuron'):
            if not 'position' in neuron:
                missedList.append((network.id, neuron['id']))

    if not missedList:
        print 'All Positions are found. Checked successfully.'
        return missedList
    else:
        return missedList


def lastSeq():
    networkList = Network.objects.all()

    print "ID\t\tmeta\t\tcheck"
    print 40*"-"    
    
    error_dev, empty_dev = [], []
    for network in networkList:
        deviceDict = network.device_dict()
        
        if deviceDict:
            items = deviceDict['visible'].items() + deviceDict['hidden'].items()
            items = sorted(items, key=lambda x: int(x[0]))
            
            if int(items[-1][0]) != deviceDict['meta']['last_seq']:
                error_dev.append("%s\t\t%s\t\t%s" %(network.id, deviceDict['meta']['last_seq'], int(items[-1][0])))
        else:
            empty_dev.append(network.devices_json)
            
    if error_dev:
        print '\n'.join(error_dev)
    else:
        print 'all devices are clean.'
            
    print 40*"-"
    print 'IDs of network without devices status'
    print empty_dev



def lastDeviceId():
    networkList = Network.objects.all()
    
    print "ID\t\tmeta\t\tcheck"
    print 40*"-"  
    
    error_dev, empty_dev = [], []
    for network in networkList:
        deviceDict = network.device_dict()
        
        if deviceDict:
            items = deviceDict['visible'].items()
            items = sorted(items, key=lambda x: int(x[0]))
            if int(items[-1][1]['id']) != deviceDict['meta']['last_device_id']:
                error_dev.append("%s\t\t%s\t\t%s" %(network.id, deviceDict['meta']['last_device_id'], int(items[-1][1]['id'])))
        else:
            empty_dev.append(network.devices_json)
            
    if error_dev:
        print '\n'.join(error_dev)
    else:
        print 'all devices are clean.'
            
    print 40*"-"
    print 'IDs of network without devices status'
    print empty_dev