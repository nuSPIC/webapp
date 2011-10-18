# -*- coding: utf-8 -*-
from __future__ import print_function

import lib.json as json
from network.models import Network
from network.helpers import id_identify

import networkx as nx
import numpy as np
import nest



STATUS_FIELDS = {
    'hh_psc_alpha': ('V_m', 'E_L', 'g_L', 'C_m', 'tau_ex', 'tau_in', 'E_Na', 'g_Na', 'E_K', 'g_K', 'Act_m', 'Act_h', 'Inact_n', 'I_e'),
    'iaf_cond_alpha': ('V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e'),
    'iaf_neuron': ('V_m', 'E_L', 'C_m', 'tau_m', 't_ref', 'V_th', 'V_reset', 'tau_syn', 'I_e'),
    'iaf_psc_alpha': ('V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'tau_syn_ex', 'tau_syn_in', 'I_e'),
    'ac_generator': ('amplitude', 'offset', 'phase', 'frequency'),
    'dc_generator': ('amplitude',),
    'noise_generator': ('mean', 'std', 'dt', 'start', 'stop'),
    'poisson_generator': ('origin', 'rate', 'start', 'stop'),
    'smp_generator': ('dc', 'ac', 'freq', 'phi'),
    'spike_generator': ('start', 'stop', 'spike_times', 'spike_weights'),
}

def networkx(edgelist, layout='neato'):
    ''' Return position of neurons in network. '''      
    G = nx.DiGraph()
    G.add_edges_from(edgelist)
    return nx.graphviz_layout(G, layout)

def exportToDatabase(SPIC_id, title, description=None, gids=[], hidden=[], fields={}):
    '''
    Export informations of all devices from NEST memory to django database and returns network object.
    
    SPIC_id argument is required to classify the network for its challenge part.
    It should be string, e.g.: '1', '2', or 'SPIC1', 'SPIC2'.
    
    gids argument is optional. If not, all models in nest memory are exported to database. e.g. gids = [2,3,4,6,7,8] 
    
    hidden argument is optional. To hide some devices write a list of its ids. e.g. hidden = [6,7,8]  
    
    fields argument is optional. In the case its empty, all non-default parameters from each device are exported
    to the database. If you want fetch a part of field:
    e.g. fields = {'iaf_neuron':('V_m', 'I_e'), 'poisson_generator':('start','stop','rate')}
    '''
    
    root_status = nest.GetStatus([0])[0]
    SPIC_id = SPIC_id.split('_')[-1]
    
    if not gids:
        gids = range(1,root_status['network_size'])
    
    network_list = Network.objects.filter(SPIC_id=SPIC_id)
    if network_list:
        local_id = int(network_list.latest('local_id').local_id) + 1
    else:
        local_id = 1
        
    network_obj = Network(user_id=0, SPIC_id=SPIC_id, local_id=local_id, title=title, duration=root_status['time'])
    if description:
        network_obj.description = description

    print("Network: SPIC_id='%s', local_id=%s, title='%s', description='%s', duration='%s'" %(network_obj.SPIC_id, network_obj.local_id, network_obj.title, network_obj.description, network_obj.duration))

    # Check the existance of Spike Detector
    for sd_gid in range(1,root_status['network_size']):
        if nest.GetStatus([sd_gid])[0]['model'] == 'spike_detector':
            break
    else:
        sd_gid = -1
            
    # Create a list of devices
    tid, vid = 1, 1
    device_list, sd_sources = {}, []
    for gid in gids:
        device_status = nest.GetStatus([gid])[0]
        label = device_status['model']
        
        if 'generator' in label:
            modeltype = 'input'
        elif 'meter' in label or 'detector' in label:
            modeltype = 'output'
        else:
            modeltype = 'neuron'
        
        # model - essential information of device
        if gid in hidden:
            model = {'label':label, 'type':modeltype}
        else:
            model = {'label':label, 'type':modeltype, 'id':vid}
            vid += 1
        
        # status - optional information of device
        status = {}
        if label in fields:
            for field in fields[label]:
                status[field] = str(device_status[field])
        elif label in STATUS_FIELDS:
            for field in STATUS_FIELDS[label]:
                if nest.GetDefaults(label)[field] != device_status[field]:
                    status[field] = str(device_status[field])
            
        # essential information of connections
        connections = {}
        if nest.FindConnections([gid]):
            connections_status = nest.GetStatus(nest.FindConnections([gid]))
            targets, delay, weight = [],[],[]
            for con in connections_status:
                if con['target'] == sd_gid:
                    sd_sources.append(str(gid))
                else:
                    targets.append(str(con['target']))
                    weight.append(str(con['weight']))
                    delay.append(str(con['delay']))
            
            if targets:
                if len(np.unique(np.array(weight))) == 1:
                    weight = np.unique(np.array(weight)).tolist()
                if len(np.unique(np.array(delay))) == 1:
                    delay = np.unique(np.array(delay)).tolist()
                
                connections['targets'] = ','.join(targets)
                connections['weight'] = ','.join(weight)
                connections['delay'] = ','.join(delay)
                
        if device_status['model'] == 'spike_detector':
            connections['sources'] = ','.join(sd_sources)
            
        # merge all information of the device
        print('%s' % tid, end=' ')
        if tid in hidden:
            print ('(hidden)', end=' ')
        print('')
        print(' - Model: %s' % model)
        print(' - Status: %s' % status)
        print(' - Connection params: %s \n' % connections)
        device_list[('%4d' %tid).replace(' ', '0')] = [model, status, connections]
        tid += 1

    while True:
        response = raw_input('Is it correct (y/[n])? ')
        if response not in ['y', 'n', '']:
            continue
        elif response == 'y':
            break
        else:
            print('aborted')
            return
    
    network_obj.devices_json = json.encode(device_list)
    network_obj.save() 

    id_filterbank = network_obj.id_filterbank()
    
    # Save position of neurons
    edgelist = network_obj.connections(modeltype='neuron')
    pos = networkx(edgelist, layout='circo')
    print(pos)
    
    if pos:
        for key, value in pos.iteritems():
            device_list[id_identify(id_filterbank, key)][0]['position'] = list(value)
            
        network_obj.devices_json = json.encode(device_list)
        network_obj.save()
    
    print('Export is successful.')

    return network_obj
    
