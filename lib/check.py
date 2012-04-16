# -*- coding: utf-8 -*-

from network.models import Network

def checkPositions(id=None, user_id=None):

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
