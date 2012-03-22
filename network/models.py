# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
import numpy as np

import lib.json as json
from network.network_settings import SPIC_CHOICES, ALL_PARAMS_ORDER
from network.helpers import values_extend, id_escape, id_identify

#from result.models import Result

class SPIC(models.Model):
    group = models.CharField(max_length=2, null=True, choices=SPIC_CHOICES)
    local_id = models.IntegerField(null=True)

    title = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.title
    

class Network(models.Model):
    user_id = models.IntegerField(null=True)
    SPIC = models.ForeignKey(SPIC, blank=True, null=True)
    local_id = models.IntegerField(null=True)

    #SPIC_id = models.CharField(max_length=6, choices=SPIC_CHOICES)
    SPIC_tmp = models.CharField(max_length=6, choices=SPIC_CHOICES)
    title = models.CharField(max_length=32)
    description = models.TextField(blank=True)

    label = models.CharField(max_length=16, blank=True, null=True, verbose_name='Title')
    date_simulated = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True)
    
    duration = models.FloatField(null=True, default=1000.0)
    status_json = models.TextField(blank=True, verbose_name='Root status')
    devices_json = models.TextField(blank=True, verbose_name='Devices')
    
    has_voltmeter = models.BooleanField()
    has_spike_detector = models.BooleanField()
    voltmeter_json = models.TextField(blank=True, verbose_name='Voltmeter')
    spike_detector_json = models.TextField(blank=True, verbose_name='Spike Detector')
    
    favorite = models.BooleanField()
    deleted = models.BooleanField()

    def __unicode__(self):
        try:
            return '%s_%s_%s' %(self.user(), self.SPIC, self.local_id)
        except:
            return '%s' %self.local_id
            
    class Meta:
        ordering = ('id',)

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

    def layout_size(self):
        x, y = 260, 12
        for dev in self.device_list(modeltype='neuron'):
            if 'position' in dev:
                pos = dev['position']
                if pos[0] > x:
                    x = pos[0]
                if pos[1] > y:
                    y = pos[1]
        return {'x':x, 'y':y}

    def id_filterbank(self):
        deviceDict = self.device_dict()
        deviceItems = deviceDict.items()
        deviceItems.sort()

        idList = []
        for tid, device in deviceItems:
            if 'id' in device:
                idList.append((tid, int(device['id'])))
            else:
                idList.append((tid, -1))
                
        return np.array(idList, dtype=int)

    def device_dict(self):
        """
        Return a dict of devices by loading JSON from the field devices_json.
        """
        if self.devices_json:
            return json.decode(str(self.devices_json))
        return {}

    def device_list(self, term='visible', modeltype=None, model=None, key=None):
        """
        Return a list of devices.
        Argument modeltype is for filtering devices by its type,
        its default is None, choices are 'neuron', 'input' or 'output'.
        """
        deviceDict = self.device_dict()
        if deviceDict:
            deviceItems = deviceDict.items()
            deviceItems.sort()
                                    
            if term == 'all':
                deviceList = [dev[1] for dev in deviceItems]
                
            elif term == 'visible':
                id_filterbank = self.id_filterbank()
                deviceList = [dev[1] for dev in deviceItems if 'id' in dev[1]]
                
                for idx, dev in enumerate(deviceList):
                    if 'targets' in dev:
                        targets = dev['targets'].split(',')
                        
                        if not 'voltmeter' in dev['model']:
                            delays = dev['delay'].split(',')
                            weights = dev['weight'].split(',')
                        else:
                            delays, weights = [], []

                        new_targets = []
                        new_weights, new_delays = [], []
                        for idx_tgt, tgt in enumerate(targets):
                            if tgt:
                                tid = ('%4d' %int(tgt)).replace(' ', '0')
                                new_tgt = id_escape(id_filterbank, tid)
                            
                                if new_tgt > 0:
                                    new_targets.append(str(new_tgt))
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
                                tid = ('%4d' %int(src)).replace(' ', '0')
                                new_src = id_escape(id_filterbank, tid)

                                if new_src > 0:
                                    new_sources.append(str(new_src))
                                
                        deviceList[idx]['sources'] = ','.join(new_sources)

            elif term == 'hidden':
                deviceList = [dev[1] for dev in deviceItems if not 'id' in dev[1]]
                
            if modeltype:
                deviceList = [dev for dev in deviceList if dev['type'] == modeltype]
            if model:
                deviceList = [dev for dev in deviceList if dev['model'] == model]
            if key:
                deviceList = [dev[key] for dev in deviceList if key in dev]
                
            return deviceList
        return []
        
        
    def update(self, deviceList):

        deviceDict = self.device_dict()
        id_filterbank = self.id_filterbank()
        layoutSize = self.layout_size()
        
        for gid, statusDict in enumerate(deviceList):
            
            # get modeltype of device.
            if statusDict['type'] == 'neuron':
                model = statusDict['model']
                
                statusDict =  dict([(key, val) for key, val in statusDict.iteritems() if val])
                if not statusDict.get('label'):
                    statusDict['label'] = model.replace("_", " ")
                
                # get true targets of neurons
                if statusDict.get('targets'):
                    extended_list = values_extend(statusDict['targets'], unique=True)
                    extended_converted_list = [str(id_identify(id_filterbank, vid)) for vid in extended_list if vid in id_filterbank[:,1]]
                    if extended_converted_list:
                        statusDict['targets'] = ','.join(extended_converted_list)
                        
                # add new ids to filterbank
                if id_filterbank.any():
                    tid = id_identify(id_filterbank, statusDict['id'])
                    if not tid:
                        tid = id_filterbank[-1][0]+1
                        id_filterbank = np.append(id_filterbank, np.array([[tid, statusDict['id']]], dtype=int), axis=0)
                else:
                    tid = 1
                    id_filterbank = np.array([[tid, statusDict['id']]], dtype=int)
                    
                # generate position of neurons if not existed
                if 'position' not in statusDict:
                    if deviceDict.get(('%4d' %tid).replace(' ', '0')):
                        if 'position' in deviceDict[('%4d' %tid).replace(' ', '0')]:
                            statusDict['position'] = deviceDict[('%4d' %tid).replace(' ', '0')]['position']
                        else:
                            statusDict['position'] = [np.random.random_integers(17, layoutSize['x']), np.random.random_integers(14, layoutSize['y']+30)]
                    else:
                        statusDict['position'] = [np.random.random_integers(17, layoutSize['x']), np.random.random_integers(14, layoutSize['y']+30)]
                
                deviceDict[('%4d' %tid).replace(' ', '0')] = statusDict
                

        for gid, statusDict in enumerate(deviceList):
            
            # get modeltype of device.
            if statusDict['type'] == 'neuron':
                continue
              
            model = statusDict['model']
            
            statusDict =  dict([(key, val) for key, val in statusDict.iteritems() if val])
            if not statusDict.get('label'):
                statusDict['label'] = model.replace("_", " ")
            
            # get true targets/sources of inputs/outputs
            if 'targets' in statusDict or 'sources' in statusDict:
                if 'targets' in statusDict:
                    term = 'targets'
                else:
                    term = 'sources'

                if statusDict[term]:
                    extended_list = values_extend(statusDict[term], unique=True)
                    extended_converted_list = [str(id_identify(id_filterbank, vid)) for vid in extended_list if vid in id_filterbank[:,1]]
                    if extended_converted_list:
                        statusDict[term] = ','.join(extended_converted_list)

                # add new ids to filterbank
                tid = id_identify(id_filterbank, statusDict['id'])
                if not tid:
                    tid = id_filterbank[-1][0]+1
                    id_filterbank = np.append(id_filterbank, np.array([[tid, statusDict['id']]], dtype=int), axis=0)
                    
                deviceDict[('%4d' %tid).replace(' ', '0')] = statusDict
       
        # update devices with true ids
        self.devices_json = json.encode(deviceDict)
        
        # create a new network if corresponding result exists,
        if self.is_recorded() or self.local_id == 0:
            network_list = Network.objects.filter(user_id=self.user_id, SPIC=self.SPIC, delete=False)
            self.local_id = network_list.latest('id').local_id + 1
            
            return Network(user_id=self.user_id, SPIC=self.SPIC, local_id=self.local_id, duration=self.duration, status_json=self.status_json, devices_json=self.devices_json)
            
        return self
        
    def device_csv_list(self):
        deviceList = self.device_list()

        lst = []
        if deviceList:
            for statusDict in deviceList:
              
                if statusDict['type'] == 'neuron' and  self.SPIC_id == '1':
                    continue

                model = statusDict['model']
                
                keyList, valList = [], []
                valJSON = '{'
                if model in ALL_PARAMS_ORDER:
                    params_order = ALL_PARAMS_ORDER[model]
                    for key in params_order:
                            
                        keyList.append(key)
                        valJSON += '"%s":' %key
                        
                        if key in statusDict:
                            valList.append(statusDict[key])
                            valJSON += '"%s",' %statusDict[key]
                        else:
                            valList.append("")
                            valJSON += '"",'
                            
                valJSON = valJSON[:-1] + '}'
                
                lst.append({'id': str(statusDict['id']), 'keyList':keyList, 'valList':valList, 'valJSON': valJSON})
                
        return lst
        
        
    def csv_list(self):
        deviceList = self.device_list()
        
        lst = []
        if deviceList:
            for statusDict in deviceList:
                if statusDict['type'] == 'neuron' and  self.SPIC.group == '1':
                    continue

                model = statusDict['model']
                if model in ALL_PARAMS_ORDER:
                    params_order = ALL_PARAMS_ORDER[model]
                    statusList = []
                    for key in params_order:
                        if key in statusDict and key not in ['label']:
                            if statusDict[key]:
                                statusList.append(str(statusDict[key]))
                            
                        
                lst.append("; ".join(statusList))
        return lst  
        
    def csv(self):
        lst = self.csv_list()
        return "\r\n".join(lst)
         

    def last_device_id(self):
        """
        Return in case of existing devices the last ID of device 
        as a marker for adding new device. Otherwise it returns None.
        """
        device_list = self.device_list()
        if device_list:
            return device_list[-1]['id']
        return 0
    
    def has_device(self, model, modeltype=None, term='visible'):
        """ Returns existence of device in the field device_json by label."""
        device_list = self.device_list(term, modeltype=modeltype, model=model)
        if device_list:
            return True
        return False

    def neuron_ids(self, model=None):
        """
        Get a list of neuron ID for connectivity matrix and
        validation check of targets/sources.
        """
        neuron_list = self.device_list(modeltype='neuron', model=model)
        if neuron_list:
            return [int(dev['id']) for dev in neuron_list]
        return neuron_list
        
    def neuron_id_filterbank(self, modeltype=None, model=None):
        neuron_list = self.device_list(modeltype='neuron')
        
        if modeltype or model:
             neuron_ids = self._connect_to(modeltype=modeltype, model=model)
             neuron_list = [neuron for neuron in neuron_list if neuron['id'] in neuron_ids]
        return np.array([[neuron['id'], gid+1] for gid, neuron in enumerate(neuron_list)])
            
    def _get_param_list(self, term):
        """
        Get a listed tuple of device ID and list of values 
        for connectivity matrix for weight or delay.
        """
        deviceList = self.device_list()
        valueList = []
        if deviceList:
            for device in deviceList:
                if term in device:
                    values = []
                    try:
                        targets = device['targets'].split(',')
                        targets = [int(tgt) for tgt in targets]
                        value = device[term].split(',')
                    except:
                        targets = []
                        
                    for neuron in self.device_list(modeltype='neuron'):
                        if int(neuron['id']) in targets:
                            try:
                                values.append(u'%s' %value[targets.index(int(neuron['id']))%len(value)])
                            except:
                                values.append(u'%s' %value[0])
                        else:
                            values.append(u' ')
                    valueList.append((device['id'], values))
        return valueList
        
    def weight_list(self):
        """ Get a listed tuple for weight. """
        return self._get_param_list('weight')
        
    def delay_list(self):
        """ Get a listed tuple of delay. """
        return self._get_param_list('delay')

    def connections(self, term='visible', data=False, modeltype=None):
        """
        Get a listed tuple of source and target in each connection.
        If data is True, it also returns dictionary of weight and delay.
        modeltype default is None, choices are 'neuron', 'input' or 'output'.
        -> see the method device_list.
        """        
        deviceList = self.device_list(term, modeltype=modeltype)
        neuron_id_filterbank = self.neuron_id_filterbank()

        connections = []
        if deviceList:
            if modeltype == 'IO_device':
                connections.extend(self.connections(term=term, data=data, modeltype='input'))
                connections.extend(self.connections(term=term, data=data, modeltype='output'))
            else:
                for gid, device in enumerate(deviceList):
                    gid += 1
                    #if 'id' in model:
                        #assert gid == int(model['id'])
                        
                    if device:
                        if 'sources' in device:
                            if len(device['sources']) > 0:
                                sources = device['sources'].split(',')
                                for index, source in enumerate(sources):
                                  
                                    if data:
                                        connections.append([int(source), gid,  {}, ''])
                                    else:
                                        connections.append([int(source), gid])
                            
                        elif 'targets' in device:
                            if len(device['targets']) > 0:
                                targets = device['targets'].split(',')
                                for index, target in enumerate(targets):
                                        
                                    if target:
                                        if modeltype == 'neuron':
                                            target = id_escape(neuron_id_filterbank, target)
                                            
                                        if data:
                                            connection_params, connection_model = {}, ''
                                            if 'weight' in device:
                                                weights = device['weight'].split(',')
                                                connection_params['weight'] = float(weights[index%len(weights)])
                                            if 'delay' in device:
                                                delays = device['delay'].split(',')
                                                connection_params['delay'] = float(delays[index%len(delays)])
                                            #if 'synapse_type' in device:
                                                #connection_models = device['synapse_type']
                                                #connection_model = connection_models[index%len(connection_models)]
                                            
                                            connections.append([gid, int(target), connection_params, connection_model])
                                        else:
                                            connections.append([gid, int(target)])
        return connections
        
    def edgelist(self):
        """ Get a list of neoron edges for graph. """
        return self.connections(data=True, modeltype='neuron')

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
            
        return neuronList
        
    def connect_to_input(self):
        """ List of connections of neurons are connected to input. """
        return self._connect_to(modeltype='input')
        
    def connect_to_output(self):
        """ List of connections of neurons are connected to output. """
        return self._connect_to(modeltype='output')    
        
    def connect_to_spike_detector(self):
        """ List of connections of neurons are connected to output. """
        return self._connect_to(model='spike_detector')            
        
    def neurons(self):
        """ Return a readable string of all meurons. """        
        neuronList = self.device_list(modeltype='neuron')
        if neuronList:
            neuronList = [(nn['model'], nn['id']) for nn in neuronList]
            if len(neuronList) < 20:
                return ", ".join(["%s [%s]"% neuron for neuron in neuronList])
            else:
                return "%s neurons" % len(neuronList)
        return ""

    def inputs(self):
        """ Return a readable string of all inputs. """        
        inputList = self.device_list(modeltype='input')
        if inputList:
            return ", ".join(["%s [%s]"%(ii['model'],ii['id']) for ii in inpuList])
        return ""
        
    def outputs(self):
        """ Return a readable string of all outputs. """        
        outputList = self.device_list(modeltype='output')
        if outputList:
            return ", ".join(["%s [%s]"%(oo['model'],oo['id']) for oo in outputList])
        return ""
        
    def iframe_height(self):
        return len(self.connect_to_spike_detector()) * 10 + 153
        
    def is_recorded(self):
        """ Check if the network is recorded. """
        return self.has_voltmeter or self.has_spike_detector

    def voltmeter_interval(self):
        """ Get the interval of measured data from voltmeter. Default is 1.0 """
        voltmeter = self.device_list(model='voltmeter')
        if 'interval' in voltmeter[0]:
            return float(voltmeter[0]['interval'])
        return 1.0

    def voltmeter_targets(self, data=False):
        """ Return a list of neurons are connected to voltmeter. """
        voltmeter = self.device_list(model='voltmeter')
        if voltmeter:
            targets = json.decode('['+ str(voltmeter[0]['targets']) + ']')
            if data:
                return [neuron for neuron in self.device_list(modeltype='neuron') if int(neuron['id']) in targets]
            return targets
        return []
   
        
    def voltmeter_points(self):
        """ Number of points in voltmeter data. Useful for quick loading of the page. """
        if self.has_voltmeter:
            V_m = json.decode(str(self.voltmeter_json))['V_m']
            return len(V_m)
        return 0

    def voltmeter_data(self, sender=None):
        """ Decode voltmeter data from json. """
        if self.has_voltmeter:
            voltmeter = self.device_list(model='voltmeter')
            if voltmeter:
                def prep_to_vis(status, values):  
                    return {'status':status, 'values': values.tolist()}
                    
                V_m = json.decode(str(self.voltmeter_json))['V_m']
                times = np.arange(1., self.duration, 1.)
                targets = json.decode('['+ str(voltmeter[0]['targets']) + ']')
                V_m = np.reshape(np.array(V_m), [self.duration-1, len(targets)]).T
                
                target_list = [target for target in self.device_list() if int(target['id']) in targets]
                if sender in targets:
                    V_m = [V_m[targets.index(sender)]]
                    target_list = [target_list[targets.index(sender)]]
                return {'V_m': map(prep_to_vis, target_list, V_m), 'times':times.tolist()}
        return {}
        
    def spike_detector_points(self):
        """ Number of points in spike detector data. Useful for quick loading of the page. """
        if self.has_spike_detector:
            return len(json.decode(str(self.spike_detector_json))['times'])
        return 0
        
    def spike_detector_data(self):
        """ Decode spike detector data from json. """
        if self.has_spike_detector:
            return json.decode(str(self.spike_detector_json))
        return []
