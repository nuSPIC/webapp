"""
# Add table network_spic in database:
manage.py syncdb --database=network

"""


import lib.json as json
from network.models import Network
import numpy as np
import uuid

from network.helpers import values_extend, id_escape, id_identify

network_list = Network.objects.all()

err = []

for network_obj in network_list:

    device_list = network_obj.device_list('all')
    if len(device_list) == 0:
        continue

    conns = network_obj.connections('all', data=True)

    id_filterbank = network_obj.id_filterbank()
    neuron_id_filterbank = network_obj.neuron_id_filterbank(model="spike_detector")


    uuids = np.unique([str(uuid.uuid4())[:5] for i in range(100)])
    synapse = ['excitatory', 'inhibitory']
    nodes = [{'id': i+1, 'uid': uuids[i], 'meta': {'visible': 0}, 'synapse': synapse['-' in device_list[i].get('weight', '')]} for i in range(len(device_list))]
    has_spike_detector, has_voltmeter = False, False

    for key in ['weight', 'targets', 'delay']:
        [(j, i.pop(key)) for j,i in enumerate(device_list) if key in i]

    pos_index = [j for j,i in enumerate(device_list) if 'position' in i]
    pos = np.array([i.pop('position') for i in device_list if 'position' in i])
    window = np.array([640.,480.])

    try:
        center = (pos.max(axis=0) + pos.min(axis=0))/2
        shift = window/2-center

        for j,i in enumerate(pos):
            nodes[pos_index[j]]['x'] = np.round(float(i[0]+shift[0]) / window[0], decimals=2)
            nodes[pos_index[j]]['y'] = np.round(float(i[1]+shift[1]) / window[1], decimals=2)
    except:
        for j,i in enumerate(pos):
            nodes[pos_index[j]]['x'] = .5
            nodes[pos_index[j]]['y'] = .5

    in_x = .05
    for j,param in enumerate(device_list):
        if 'id' in param:
            if param['type'] == 'input':
                nodes[j]['y'] = .05
                nodes[j]['x'] = in_x
                in_x += .1
            elif param['label'] == 'spike_detector':
                has_spike_detector = True
                nodes[j]['x'] = .95
                nodes[j]['y'] = .95
            elif param['label'] == 'voltmeter':
                has_voltmeter = True
                nodes[j]['x'] = .05
                nodes[j]['y'] = .95
            nodes[j]['meta']['visible'] = 1
            del param['id']

        if 'type' in param:
            nodes[j]['type'] = param.pop('type')
        if 'label' in param:
            label = param.pop('label')
            if network_obj.SPIC.group == '1' and nodes[j]['type'] == 'neuron':
                nodes[j]['label'] = 'Neuron'
                nodes[j]['disabled'] = 1
            else:
                nodes[j]['label'] = ' '.join([i.capitalize() for i in label.split('_')])
                nodes[j]['disabled'] = 0
        if 'sources' in param:
            del param['sources']
        if 'synapse_type' in param:
            del param['synapse_type']

        nodes[j]['status'] = param

    if not has_spike_detector:
        nodes.append({
            'uid': uuids[nodes[-1]['id']], 
            'id': nodes[-1]['id']+1, 
            'label': 'Spike Detector', 
            'x': .95, 'y': .95, 
            'type': 'output',
            'disabled': 0,
            'meta': {'visible': 1}, 
            'status':{'model': 'spike_detector'}})

    if not has_voltmeter:
        nodes.append({
            'uid': uuids[nodes[-1]['id']], 
            'id': nodes[-1]['id']+1, 
            'label': 'Voltmeter', 
            'x': .05, 'y': .95, 
            'type': 'output', 
            'disabled': 0,
            'meta': {'visible': 1}, 
            'status':{'model': 'voltmeter'}})

    links = [{'source': uuids[i[0]-1], 'target': uuids[i[1]-1]} for i in conns]

    for j, conn in enumerate(conns):
        for key in ['delay', 'weight']:
            links[j][key] = conn[2].get(key, 1.)
        if conn[3] != '':
            syn = {}
            for idx, s in conn[3]['syn_params'].iteritems():
                syn[idx] = float(s)
            links[j]['synapse'] = {'model': conn[3]['model'], 'status': syn}

    network_obj.nodes_json = json.encode(nodes)
    network_obj.links_json = json.encode(links)

    n2 = network_obj.nodes()
    l2 = network_obj.links()
    network_obj.update(n2, l2)

    n3 = network_obj.nodes('all')
    l3 = network_obj.links('all', out='object')
    nodes_uid = [node['uid'] for node in n3]
    nodes_sd = [n3[nodes_uid.index(link['source'])] for link in links if n3[nodes_uid.index(link['target'])]['status']['model'] == 'spike_detector']
    nodes_sd_id = [node['id'] for node in nodes_sd]

    if len(network_obj.spike_detector_json) > 0:
        data = json.decode(str(network_obj.spike_detector_json))

        data['senders'] = [int(id_escape(id_filterbank, sender)) for sender in data['senders']]
        assert np.in1d(np.unique(data['senders']).tolist(), nodes_sd_id).all()

        neurons = [{'id': s, 'uid': u'%s' %(nodes_sd[nodes_sd_id.index(s)]['uid'])} for s in np.unique(data['senders']).tolist()]
        data['meta'] = {'neurons': neurons}

        network_obj.spike_detector_json = json.encode(data)

    if network_obj.has_voltmeter:
        data = json.decode(str(network_obj.voltmeter_json))

        neurons = [{'uid': link['target']['uid'], 'id': link['target']['id']} for link in l3 if link['source']['status']['model'] == 'voltmeter']
        data['meta'] = {'neurons': neurons}

        network_obj.voltmeter_json = json.encode(data)


    network_obj.save()


