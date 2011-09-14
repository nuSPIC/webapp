# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

import lib.json as json

__all__ = ["Network"]

SPIC_CHOICES = (('1','SPIC1'),
                ('2','SPIC2'),
                ('3','SPIC3'),
                ('4','SPIC4'))

class Network(models.Model):
    user_id = models.IntegerField()
    SPIC_id = models.CharField(max_length=6, choices=SPIC_CHOICES)
    local_id = models.IntegerField()
    
    title = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    
    duration = models.FloatField(null=True, default=1000.0)
    status_json = models.TextField(blank=True, verbose_name='Root status')
    devices_json = models.TextField(blank=True, verbose_name='Devices')

    def __unicode__(self):
        return '%s_%s_%s' %(self.user(), self.get_SPIC_id_display(), self.local_id)

    def user(self):
        """
        Get user object from the django model 'auth' by user_id.
        CAUTION: the model 'auth' might be stored in other database.
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

    def device_list(self, term='visible', modeltype=None, label=None):
        """
        Return a list of devices by loading JSON from the field devices_json.
        Argument modeltype is for filtering devices by its type,
        its default is None, choices are 'neuron', 'input' or 'output'.
        """
        if self.devices_json:
            devices = json.decode(str(self.devices_json))
            
            if term == 'visible':
                devices = [dev for dev in devices if 'id' in dev[0]]
            elif term == 'hidden':
                devices = [dev for dev in devices if not 'id' in dev[0]]
            if modeltype:
                devices = [dev for dev in devices if dev[0]['type']==modeltype]
            if label:
                devices = [dev for dev in devices if dev[0]['label']==label]
            return devices
        return []
    
    def last_device_id(self):
        """
        Return in case of existing devices the last ID of device 
        as a marker for adding new device. Otherwise it returns None.
        """
        device_list = self.device_list()
        if device_list:
            return device_list[-1][0]['id']
        return 0
    
    def has_device(self, label, modeltype=None, term='visible'):
        """ Returns existence of device in the field device_json by label."""
        device_list = self.device_list(term, modeltype=modeltype, label=label)
        if device_list:
            return True
        return False

    def neuron_ids(self):
        """
        Get a list of neuron ID for connectivity matrix and
        validation check of targets/sources.
        """
        neuron_list = self.device_list(modeltype='neuron')
        if neuron_list:
            return [int(dev[0]['id']) for dev in neuron_list]
        return neuron_list
        
    def _get_param_list(self, term):
        """
        Get a listed tuple of device ID and list of values 
        for connectivity matrix for weight or delay.
        """
        device_list = self.device_list()
        value_list = []
        if device_list:
            for model, status, params in device_list:
                if term in params:
                    values = []
                    try:
                        targets = params['targets'].split(',')
                        targets = [int(tgt) for tgt in targets]
                        value = params[term].split(',')
                    except:
                        targets = []
                        
                    for neuron_model, neuron_status, neuron_params in self.device_list(modeltype='neuron'):
                        if int(neuron_model['id']) in targets:
                            try:
                                values.append(u'%s' %value[targets.index(int(neuron_model['id']))%len(value)])
                            except:
                                values.append(u'%s' %value[0])
                        else:
                            values.append(u' ')
                    value_list.append((model['id'], values))
        return value_list
        
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
        device_list = self.device_list(term, modeltype=modeltype)
        connections = []
        if device_list:
            if modeltype == 'IO_device':
                connections.extend(self.connections(term=term, data=data, modeltype='input'))
                connections.extend(self.connections(term=term, data=data, modeltype='output'))
            else:
                for gid, device in enumerate(device_list):
                    model, status, params = device
                    gid += 1
                    if 'id' in model:
                        assert gid == int(model['id'])
                    if params:
                        if model['label'] == u'spike_detector':
                            if len(params['sources']) > 0:
                                sources = params['sources'].split(',')
                                for index, source in enumerate(sources):
                                    if data:
                                        connections.append([int(source), gid,  None])
                                    else:
                                        connections.append([int(source), gid])
                            
                        else:
                            if len(params['targets']) > 0:
                                targets = params['targets'].split(',')
                                for index, target in enumerate(targets):
                                    if data:
                                        connection_params = {}
                                        if 'weight' in params:
                                            weights = params['weight'].split(',')
                                            connection_params['weight'] = float(weights[index%len(weights)])
                                        if 'delay' in params:
                                            delays = params['delay'].split(',')
                                            connection_params['delay'] = float(delays[index%len(delays)])
                                            
                                        if connection_params: 
                                            connections.append([gid, int(target), connection_params])
                                        else:
                                            connections.append([gid, int(target), {}])
                                    else:
                                        connections.append([gid, int(target)])
        return connections
        
    def edgelist(self):
        """ Get a list of neoron edges for graph. """
        return self.connections(data=True, modeltype='neuron')

    def _connect_to(self, modeltype):
        """ Get a list of devices of one type, which the neurons are connected to. """
        device_list = self.device_list(modeltype=modeltype)
        neurons = []
        for model, status, params in device_list:
            if 'targets' in params:
                neurons.extend(params['targets'].split(','))
            else:
                neurons.extend(params['sources'].split(','))
        if neurons:
            neurons = [int(nn) for nn in neurons if nn != '']
        return list(set(neurons))
        
    def connect_to_input(self):
        """ List of connections of neurons are connected to input. """
        return self._connect_to('input')
        
    def connect_to_output(self):
        """ List of connections of neurons are connected to output. """
        return self._connect_to('output')        
        
    def neurons(self):
        """ Return a readable string of all meurons. """        
        neuron_list = self.device_list(modeltype='neuron')
        if neuron_list:
            neuron_list = [(nn[0]['label'], nn[0]['id']) for nn in neuron_list]
            if len(neuron_list) < 20:
                return ", ".join(["%s [%s]"% neuron for neuron in neuron_list])
            else:
                return "%s neurons" % len(neuron_list)
        return ""

    def inputs(self):
        """ Return a readable string of all inputs. """        
        input_list = self.device_list(modeltype='input')
        if input_list:
            return ", ".join(["%s [%s]"%(ii[0]['label'],ii[0]['id']) for ii in input_list])
        return ""
        
    def outputs(self):
        """ Return a readable string of all outputs. """        
        output_list = self.device_list(modeltype='output')
        if output_list:
            return ", ".join(["%s [%s]"%(oo[0]['label'],oo[0]['id']) for oo in output_list])
        return ""