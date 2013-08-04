# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
import numpy as np

import lib.json as json


from network.network_settings import SPIC_CHOICES, ALL_PARAMS_ORDER


from network.helpers import values_extend, id_escape, id_identify

class SPIC(models.Model):
    group = models.CharField(max_length=2, null=True, choices=SPIC_CHOICES)
    local_id = models.IntegerField(null=True)

    title = models.CharField(max_length=32, default='')
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.title


class Network(models.Model):
    user_id = models.IntegerField(null=True)
    SPIC = models.ForeignKey(SPIC, blank=True, null=True)
    local_id = models.IntegerField(null=True)

    label = models.CharField(max_length=16, blank=True, null=True)
    date_simulated = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True)

    duration = models.FloatField(null=True, default=1000.0)
    status_json = models.TextField(blank=True, verbose_name='Root status')
    devices_json = models.TextField(blank=True, verbose_name='Devices')

    nodes_json = models.TextField(blank=True, verbose_name='Nodes')
    links_json = models.TextField(blank=True, verbose_name='Links')

    has_voltmeter = models.BooleanField()
    has_spike_detector = models.BooleanField()
    voltmeter_json = models.TextField(blank=True, verbose_name='Voltmeter')
    spike_detector_json = models.TextField(blank=True, verbose_name='Spike Detector')

    favorite = models.BooleanField()
    deleted = models.BooleanField()

    class Meta:
        ordering = ('user_id', 'SPIC', 'local_id')

    def __unicode__(self):
        try:
            return '%s_%s_%s' %(self.user_id, self.SPIC, self.local_id)
        except:
            return '%s' %self.pk

    def copy(self):
        new_kwargs = dict([(fld.name, getattr(self, fld.name)) for fld in self._meta.fields if fld.name != 'id']);
        return self.__class__.objects.create(**new_kwargs)

    def user(self):
        """
        Get user object from the django model 'auth' by user_id.
        CAUTION: the model 'User' is stored in other database.
        """
        if self.user_id == 0:
            return 'architect'
        else:
            return User.objects.get(pk=self.user_id)

    def root_status(self):
        """ Returns status data from the field status_json."""
        if self.status_json:
            return json.decode(str(self.status_json))
        return {}

    def nodes(self, term='visible', meta=False, key=None):
        if len(self.nodes_json) == 0: return []

        nodes = json.decode(self.nodes_json)

        # Get visible, hidden or all nodes
        if term == 'visible':
            nodes = filter(lambda node: (node['meta']['visible'] == 1), nodes)
        elif term == 'hidden':
            nodes = filter(lambda node: (node['meta']['visible'] == 0), nodes)

        # Meta data should not be visible for users
        if meta is False:
            for index in range(len(nodes)):
                del nodes[index]['meta']

        # Recounting ID
        for index in range(len(nodes)):
            nodes[index]['id'] = index+1

        # If key, get a list of its values
        if key:
            nodes = [node[key] for node in nodes if key in node]

        return nodes

    def nodes_csv(self):
        if len(self.nodes_json) == 0: return ""

        nodes = self.nodes()

        lst = []
        if nodes:
            for node in nodes:
                if node['type'] == 'neuron' and  self.SPIC.group == '1':
                    continue

                model = node['status']['model']
                if model in ALL_PARAMS_ORDER:
                    params_order = ALL_PARAMS_ORDER[model]
                    statusList = []
                    for key in params_order:
                        if key == 'id':
                            statusList.append(str(node.get(key)))
                        elif key in node['status']:
                            if node['status'][key]:
                                statusList.append(str(node['status'].get(key)))

                lst.append("; ".join(statusList))
        return "\r\n".join(lst)

    def neuron_ids(self):
        """
        Get a list of neuron ID for connectivity matrix and
        validation check of targets/sources.
        """
        nodes = [node for node in self.nodes() if node['type'] == 'neuron']
        if nodes:
            return [int(node['id']) for node in nodes]
        return []

    def links(self, term='visible', key=None, out='uid'):
        if len(self.links_json) == 0: return []

        links = json.decode(self.links_json)

        # Get nodes
        nodes = self.nodes(term)
        nodes_uid = [node['uid'] for node in nodes]

        # Get visible, hidden or all links
        if term == 'visible' or term == 'hidden':
            if term == 'visible':
                links = filter(lambda link: (link['source'] in nodes_uid and link['target'] in nodes_uid), links)
            if term == 'hidden':
                links = filter(lambda link: (link['source'] in nodes_uid or link['target'] in nodes_uid), links)

        # Output of source and target values
        if out == 'object':
            for index in range(len(links)):
                links[index]['source'] = nodes[nodes_uid.index(links[index]['source'])]
                links[index]['target'] = nodes[nodes_uid.index(links[index]['target'])]
        elif out != 'uid':
            for index in range(len(links)):
                if out in nodes[nodes_uid.index(links[index]['source'])]:
                    links[index]['source'] = nodes[nodes_uid.index(links[index]['source'])][out]
                if out in nodes[nodes_uid.index(links[index]['target'])]:
                    links[index]['target'] = nodes[nodes_uid.index(links[index]['target'])][out]

        # If key, get a list of its values
        if key:
            links = [link[key] for link in links if key in link]

        return links

    def update(self, nodes, links=None):

        # Add meta to visible nodes
        for index in range(len(nodes)):
            nodes[index]['meta'] = {'visible': 1}

        # Add hidden nodes
        nodes = sorted(nodes, key=lambda node: node['id'])
        nodes_hidden = self.nodes('hidden', meta=True)
        nodes += nodes_hidden

        # Recounting ID
        for index in range(len(nodes)):
            nodes[index]['id'] = index+1

        self.nodes_json = json.encode(nodes)

        if links:
            # Add hidden links
            links_hidden = self.links('hidden')
            links += links_hidden

            # Filter links
            nodes_uid = [node['uid'] for node in nodes]
            links = filter(lambda link: (link['source'] in nodes_uid and link['target'] in nodes_uid), links)

            for idx, val in enumerate(links):
                links[idx]['weight'] = float(val['weight'])
                links[idx]['delay'] = float(val['delay'])

            self.links_json = json.encode(links)

    def is_recorded(self):
        """ Check if the network is recorded. """
        return self.has_voltmeter or self.has_spike_detector

    def spike_detector_data(self, return_index=False):
        """ Decode spike detector data from json. """

        connect_to = [link['source']['id'] for link in self.links(out='object') if link['target']['status']['model'] == 'spike_detector']
        meta = {'neurons': [], 'simTime': self.duration, 'connect_to': connect_to}

        if self.has_spike_detector:
            data = json.decode(str(self.spike_detector_json))
            assert len(data['senders']) == len(data['times'])

            meta['neurons'] = data['meta']['neurons']
            data['meta'] = meta

            if return_index:
                senders = np.array(data['senders'])
                for idx, val in enumerate(meta['neurons']):
                    senders[senders==val['id']] = idx
                    data['meta']['neurons'][idx]['idx'] = idx
                data['senders'] = senders.tolist()
            return data

        return {'meta': meta}

    def spike_detector_data_index(self):
        return self.spike_detector_data(return_index=True)

    def voltmeter_data(self, sender=None):
        """ Decode voltmeter data from json. """

        connect_to = [link['target']['id'] for link in self.links(out='object') if link['source']['status']['model'] == 'voltmeter']
        meta = {'neurons': [], 'connect_to': connect_to}

        if self.has_voltmeter:
            def prep_to_vis(values):
                return {'values': values.tolist(), 'values_reduced': values[::5].tolist()}

            if len(self.voltmeter_json) > 0:
                vm_E = json.decode(str(self.voltmeter_json))
            else:
                vm_E = {'meta':{'neurons': []}, 'V_m': ''}
            meta['neurons'] = vm_E['meta']['neurons']

            V_m = vm_E['V_m']
            if len(V_m) > 0:
                V_m = np.reshape(np.array(V_m), [-1, len(meta['neurons'])]).T
            times = np.arange(1., self.duration, 1.)

            data = {'V_m': map(prep_to_vis, V_m), 'times':times.tolist(), 'times_reduced':times[::5].tolist()}
            data['meta'] = meta
            return data

        return {'meta': meta}





        """
        outdated
        """

    def _connect_to(self, modeltype=None, model=None):
        """ Get a list of devices of one type, which the neurons are connected to. """
        deviceList = self.device_list(modeltype=modeltype, model=model)

        neuronList = []
        if deviceList:
            for device in deviceList:
                if 'targets' in device:
                    neuronList.extend(device['targets'].split(','))
                else:
                    neuronList.extend(device['sources'].split(','))

        if neuronList:
            neuronList = [int(nn) for nn in neuronList if nn != '']
            neuronList = list(set(neuronList))
            neuronList = sorted(neuronList, key=lambda x: int(x))

        return neuronList

    def connect_to_input(self):
        """ List of connections of neurons are connected to input. """
        return self._connect_to(modeltype='input')

    def connect_to_output(self):
        """ List of connections of neurons are connected to output. """
        return self._connect_to(modeltype='output')

    def connections(self, mode='visible', data=False, modeltype=None):
        """
        Get a listed tuple of source and target in each connection.
        If data is True, it also returns dictionary of weight and delay.
        modeltype default is None, choices are 'neuron', 'input', 'output' or 'IO_device'.
        -> see the method device_list.
        """ 

        if modeltype == 'IO_device':
            return self.connections(mode, data, 'input') + self.connections(mode, data, 'output')
        else:
            if mode == 'visible':
                deviceList = self.device_list(modeltype=modeltype)
                deviceItems = [dev for dev in enumerate(deviceList)]
            else:
                deviceItems = self.device_items(mode, modeltype)

            if deviceItems:
                connections = []
                for idx, device in deviceItems:
                    if device:
                        if mode == 'visible':
                            device_id = device['id']
                        else:
                            device_id = int(idx)

                        if 'sources' in device:
                            if len(device['sources']) > 0:
                                sources = device['sources'].split(',')
                                for index, source in enumerate(sources):

                                    if data:
                                        connections.append([int(source), device_id,  {}, ''])
                                    else:
                                        connections.append([int(source), device_id])

                        elif 'targets' in device:
                            if len(device['targets']) > 0:
                                targets = device['targets'].split(',')
                                for index, target in enumerate(targets):

                                    if target:
                                        if data:
                                            connection_params, connection_model = {}, ''
                                            if 'weight' in device:
                                                weights = device['weight'].split(',')
                                                connection_params['weight'] = float(weights[index%len(weights)])
                                            if 'delay' in device:
                                                delays = device['delay'].split(',')
                                                connection_params['delay'] = float(delays[index%len(delays)])
                                            if 'synapse_type' in device:
                                                connection_models = device['synapse_type']
                                                connection_model = connection_models[index%len(connection_models)]

                                            connections.append([device_id, int(target), connection_params, connection_model])
                                        else:
                                            connections.append([device_id, int(target)])
                return connections

    def device_dict(self):
        """
        Return a dict of devices by loading JSON from the field devices_json.
        """
        if self.devices_json:
            return json.decode(str(self.devices_json))
        return {}

    def device_items(self, mode='visible', modeltype=None, model=None):
        """
        Return a sorted items of devices.
        Argument modeltype is for filtering devices by its type or by model,
        Its argument default is None, possible choices are 'neuron', 'input' or 'output'.
        """
        deviceDict = self.device_dict()

        if deviceDict:
            if mode == 'all':
                deviceItems = deviceDict['visible'].items() + deviceDict['hidden'].items()
            elif mode == 'visible':
                deviceItems = deviceDict['visible'].items()
            elif mode == 'hidden':
                deviceItems = deviceDict['hidden'].items()

            deviceItems = sorted(deviceItems, key=lambda x: int(x[0]))
            # Filter by argument
            if modeltype:
                deviceItems = [dev for dev in deviceItems if dev[1]['type'] == modeltype]
            if model:
                deviceItems = [dev for dev in deviceItems if dev[1]['model'] == model]
            return deviceItems
        return []

    def device_list(self, mode='visible', key=None, **kwargs):
        """
        Return a list of devices.
        """
        kwargs['mode'] = mode
        deviceItems = self.device_items(**kwargs)

        if deviceItems:
            deviceList = [dev[1] for dev in deviceItems]

            if mode == 'visible':
                id_filterbank = self.id_filterbank()

                for idx, dev in enumerate(deviceList):
                    if 'targets' in dev:
                        targets = dev['targets'].split(',')

                        delays, weights = [], []
                        if not 'voltmeter' in dev['model']:
                            if 'delay' in dev:
                                delays = dev['delay'].split(',')
                            if 'weight' in dev:
                                weights = dev['weight'].split(',')

                        new_targets = []
                        new_weights, new_delays = [], []
                        for idx_tgt, tgt in enumerate(targets):
                            if tgt:
                                if mode == 'visible':
                                    tgt = id_escape(id_filterbank, tgt)

                                if int(tgt) > 0:
                                    new_targets.append(str(tgt))
                                    if len(weights) > 1:
                                        new_weights.append(weights[idx_tgt])
                                    elif weights:
                                        new_weights = weights

                                    if len(delays) > 1:
                                        new_delays.append(delays[idx_tgt])
                                    elif delays:
                                        new_delays = delays

                        deviceList[idx]['targets'] = ','.join(new_targets)

                        if not 'voltmeter' in dev['model']:
                            deviceList[idx]['weight'] = ','.join(new_weights)
                            deviceList[idx]['delay'] = ','.join(new_delays)

                    if 'sources' in dev:
                        sources = dev['sources'].split(',')

                        new_sources = []
                        for idx_src, src in enumerate(sources):
                            if src:
                                if mode == 'visible':
                                    src = id_escape(id_filterbank, src)

                                if int(src) > 0:
                                    new_sources.append(str(src))
                                
                        deviceList[idx]['sources'] = ','.join(new_sources)

            if key:
                return [dev[key] for dev in deviceList if key in dev]
            return deviceList
        return []

    def id_filterbank(self):
        deviceItems = self.device_items('all')

        idList = []
        for tid, device in deviceItems:
            if 'id' in device:
                idList.append((tid, int(device['id'])))
            else:
                idList.append((tid, -1))

        return np.array(idList, dtype=int)



    def neuron_id_filterbank(self, modeltype=None, model=None):
        neuron_list = self.device_list(modeltype='neuron')
        
        if modeltype or model:
             neuron_ids = self._connect_to(modeltype=modeltype, model=model)
             neuron_list = [neuron for neuron in neuron_list if neuron['id'] in neuron_ids]
        return np.array([[neuron['id'], gid+1] for gid, neuron in enumerate(neuron_list)])

#    def save(self, *args, **kwargs):
#        # correct sequence in strict steps ordering
#        deviceDict = self.device_dict()
#        if 'visible' in deviceDict or 'hidden' in deviceDict:
#            visible, hidden = deviceDict['visible'], deviceDict['hidden']

#            seqList = hidden.keys() + visible.keys()
#            if seqList:
#                seqList = sorted(seqList, key=lambda x: int(x))
#                if len(seqList) != int(seqList[-1]):
#                    seq_update = dict([(old_seq, str(new_seq+1)) for new_seq, old_seq in enumerate(seqList)])

#                    deviceItems = hidden.items() + visible.items()
#                    deviceItems = sorted(deviceItems, key=lambda x: int(x[0]))

#                    visible, hidden, last_device_id = {}, {}, 0
#                    for seq, statusDict in deviceItems:
#                        if 'targets' in statusDict or 'sources' in statusDict:
#                            if 'targets' in statusDict:
#                                key = 'targets'
#                            else:
#                                key = 'sources'

#                            if statusDict[key]:
#                                connList = statusDict[key].split(',')
#                                connList = [str(seq_update[str(conn)]) for conn in connList if conn in seq_update]
#                                statusDict[key] = ','.join(connList)

#                        if 'id' in statusDict:
#                            visible[seq_update[str(seq)]] = statusDict
#                            last_device_id = statusDict['id']
#                        else:
#                            hidden[seq_update[str(seq)]] = statusDict
#                        last_seq = seq_update[str(seq)]

#                    # update meta data
#                    meta = {'last_seq':int(last_seq), 'last_device_id':int(last_device_id)}
#                    self.devices_json = json.encode({'visible': visible, 'hidden': hidden, 'meta': meta})
#            else:
#                self.devices_json = u''
#        super(Network, self).save(*args, **kwargs)


#    def update(self, deviceList, force_self=False):
#        """
#        Get device list, worked through filterbank and update device json.
#        In case it is recorded it returns a new network object. Otherwise it returns itself.
#        """

#        deviceDict = self.device_dict()

#        # get last sequence
#        id_filterbank = self.id_filterbank()
#        if 'meta' in deviceDict:
#            last_seq = int(deviceDict['meta']['last_seq'])
#        elif id_filterbank.any():
#            last_seq = int(id_filterbank[-1][0])
#        else:
#            last_seq = 0

#        # refresh filterbank
#        last_device_id = 0
#        for idx, statusDict in enumerate(deviceList):
#            last_device_id = statusDict['id']

#            seq = id_identify(id_filterbank, statusDict['id'])
#            if seq <= 0:
#                last_seq += 1
#                # add new ids to filterbank
#                if id_filterbank.any():
#                    id_filterbank = np.append(id_filterbank, np.array([[last_seq, statusDict['id']]], dtype=int), axis=0)
#                else:
#                    id_filterbank = np.array([[last_seq, statusDict['id']]], dtype=int)

#        # update status of neurons
#        visible = {}
#        for statusDict in deviceList:

#            # get modeltype of device.
#            if statusDict['type'] == 'neuron':
#                model = statusDict['model']

#                statusDict =  dict([(key, val) for key, val in statusDict.iteritems() if val])
#                if not statusDict.get('label'):
#                    statusDict['label'] = model.replace("_", " ")

#                # get true targets of neurons
#                if statusDict.get('targets'):
#                    extended_list = values_extend(statusDict['targets'], unique=True)
#                    extended_converted_list = [str(id_identify(id_filterbank, idx)) for idx in extended_list if idx in id_filterbank[:,1]]
#                    if extended_converted_list:
#                        statusDict['targets'] = ','.join(extended_converted_list)

#                # add new ids to filterbank
#                seq = id_identify(id_filterbank, statusDict['id'])

#                visible[str(seq)] = statusDict

#        # update status of inputs/outputs
#        for statusDict in deviceList:

#            # get modeltype of device.
#            if statusDict['type'] == 'neuron':
#                continue

#            model = statusDict['model']
#            statusDict =  dict([(key, val) for key, val in statusDict.iteritems() if val])
#            if not statusDict.get('label'):
#                statusDict['label'] = model.replace("_", " ")

#            # get true targets/sources of inputs/outputs
#            if 'targets' in statusDict or 'sources' in statusDict:
#                if 'targets' in statusDict:
#                    key = 'targets'
#                else:
#                    key = 'sources'

#                if statusDict[key]:
#                    extended_list = values_extend(statusDict[key], unique=True)
#                    extended_converted_list = [str(id_identify(id_filterbank, idx)) for idx in extended_list if idx in id_filterbank[:,1]]
#                    if extended_converted_list:
#                        statusDict[key] = ','.join(extended_converted_list)

#            # add new ids to filterbank
#            seq = id_identify(id_filterbank, statusDict['id'])
#            visible[str(seq)] = statusDict

#        # get status of hidden devices
#        if 'hidden' in deviceDict:
#            hidden = deviceDict['hidden']
#        else:
#            hidden = {}

#        # update meta data
#        meta = {'last_seq':int(last_seq), 'last_device_id':int(last_device_id)}
#        devices_json = json.encode({'visible': visible, 'hidden': hidden, 'meta':meta})

#        # create a new network if its corresponding result exists or if it is initial network.
#        if (self.is_recorded() or self.local_id == 0) and not force_self:
#            network_list = Network.objects.filter(user_id=self.user_id, SPIC=self.SPIC, deleted=False)
#            local_id = network_list.latest('id').local_id + 1
#            return Network(user_id=self.user_id, SPIC=self.SPIC, local_id=local_id, duration=self.duration, status_json=self.status_json, devices_json=devices_json)
#        else:
#            # update devices with true ids
#            self.devices_json = devices_json
#            return self



