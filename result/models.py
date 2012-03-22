# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from network.models import Network
from reversion.models import Revision

import lib.json as json
import numpy as np


class Result(models.Model):
    revision = models.OneToOneField(Revision)
    local_id = models.IntegerField(default=1)
    
    date_simulated = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    favorite = models.BooleanField()

    has_voltmeter = models.BooleanField()
    voltmeter_json = models.TextField(blank=True, verbose_name='Voltmeter')
    
    has_spike_detector = models.BooleanField()
    spike_detector_json = models.TextField(blank=True, verbose_name='Spike Detector')
    
    def __unicode__(self):
        return '%s - %s' %(self.local_id, self.date_simulated)

    class Meta:
        ordering = ('id',)

    @property
    def network(self):
        """ Get the network for this result. """
        return self.revision.version_set.all()[0].object_version.object

    def is_recorded(self):
        """ Check if the network is recorded. """
        return self.has_voltmeter or self.has_spike_detector

    def voltmeter_interval(self):
        """ Get the interval of measured data from voltmeter. Default is 1.0 """
        voltmeter = self.network.device_list(model='voltmeter')
        if 'interval' in voltmeter[0]:
            return float(voltmeter[0]['interval'])
        return 1.0

    def voltmeter_targets(self, data=False):
        """ Return a list of neurons are connected to voltmeter. """
        network_obj = self.network
        voltmeter = network_obj.device_list(model='voltmeter')
        if voltmeter:
            targets = json.decode('['+ str(voltmeter[0]['targets']) + ']')
            if data:
                return [neuron for neuron in network_obj.device_list(modeltype='neuron') if int(neuron['id']) in targets]
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
            network_obj = self.network
            voltmeter = network_obj.device_list(model='voltmeter')
            if voltmeter:
                def prep_to_vis(status, values):  
                    return {'status':status, 'values': values.tolist()}
                    
                V_m = json.decode(str(self.voltmeter_json))['V_m']
                times = np.arange(1., network_obj.duration, 1.)
                targets = json.decode('['+ str(voltmeter[0]['targets']) + ']')
                V_m = np.reshape(np.array(V_m), [network_obj.duration-1, len(targets)]).T
                
                target_list = [target for target in network_obj.device_list() if int(target['id']) in targets]
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
