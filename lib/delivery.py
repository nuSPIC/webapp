# -*- coding: utf-8 -*-
from network.models import Network

import networkx as nx
import numpy as np
import nest

import cjson

STATUS_FIELDS = {
    'Neuron': (),
        'aeif_cond_alpha': (),
        'iaf_cond_alpha': (),
        'iaf_psc_alpha': ('I_e','tau_m', 'V_th', 'E_L', 't_ref', 'V_reset', 'C_m', 'V_m'),
        'iaf_neuron': (),
    'Input': ('start', 'stop'),
        'ac_generator': ('amplitude', 'frequency'),
        'dc_generator': (),
        'noise_generator': ('mean', 'std'),
        'poisson_generator': ('rate', ),
    'Output': (),
        'spike_detector': (),
        'voltmeter': (),
}

def networkx(edgelist, layout='neato'):
    """ Return position of neurons in network. """      
    G = nx.DiGraph()
    G.add_edges_from(edgelist)
    return nx.graphviz_layout(G, layout)

def NEST_to_nuSPIC(SPIC_id):
    """transfer status informations
    from nest models to django database """
    
    root_status = nest.GetStatus([0])[0]
    
    SPIC_id = SPIC_id.split('_')[-1]
    
    if Network.objects.filter(SPIC_id=SPIC_id):
        local_id = Network.objects.filter(SPIC_id=SPIC_id).latest('local_id').local_id + 1
    else:
        local_id = 1
    network_obj, created = Network.objects.get_or_create(user_id=0, SPIC_id=SPIC_id, local_id=local_id)
    
    if created:
        network_obj.duration = root_status['time']
        
        
        for sd_gid in range(1,root_status['network_size']):
            if nest.GetStatus([sd_gid])[0]['model'] == 'spike_detector':
                break
        else:
            sd_gid = -1
                
        device_list, sd_sources = [], []
        for gid in range(1,root_status['network_size']):
            device_status = nest.GetStatus([gid])[0]
            
            if 'generator' in device_status['model']:
                modeltype = 'input'
            elif 'meter' in device_status['model'] or 'detector' in device_status['model']:
                modeltype = 'output'
            else:
                modeltype = 'neuron'
            
            model = {'label':device_status['model'], 'type':modeltype, 'id':gid}
            
            status = {}
            for field in STATUS_FIELDS[device_status['model']]:
                status[field] = device_status[field]
                
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
                
            device_list.append([gid, model, status, connections])
            
        edgelist = network_obj.connections(modeltype='neuron')
        pos = networkx(edgelist, layout='circo')

        for gid,value in pos.items():
            if int(device_list[gid-1][0]['id']) == gid:
                device_list[gid-1][0]['position'] = list(value)
                
        network_obj.devices_json = cjson.encode(device_list)
        network_obj.save()

    return network_obj, created
    
