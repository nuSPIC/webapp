from django.db import models
from reversion.models import Revision

import numpy as np
import cjson

from network.templatetags.network_filters import readable

class Result(models.Model):
    revision = models.OneToOneField(Revision)
    local_id = models.IntegerField(default=1)
    
    date_simulated = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)

    has_voltmeter = models.BooleanField()
    voltmeter_json = models.TextField(blank=True, verbose_name='Voltmeter')
    
    has_spike_detector = models.BooleanField()
    spike_detector_json = models.TextField(blank=True, verbose_name='Spike Detector')
    
    def __unicode__(self):
        return '%s - %s' %(self.local_id, self.date_simulated)

    @property
    def network(self):
	return self.revision.version_set.all()[0].object_version.object

    def revision_date_created(self):
	return self.revision.date_created

    def is_recorded(self):
	return self.has_voltmeter or self.has_spike_detector

    def voltmeter_interval(self):
	voltmeter = self.network.device_list(label='voltmeter')
	if 'interval' in voltmeter[0][1]:
	    return float(voltmeter[0][1]['interval'])
	return 1.0

    def voltmeter_targets(self, data=True):
	voltmeter = self.network.device_list(label='voltmeter')
	if voltmeter:
	    targets = cjson.decode('['+ voltmeter[0][2]['targets'] + ']')
	    if data:
		return [neuron for neuron in self.network.device_list(modeltype='neuron') if int(neuron[0]['id']) in targets]
	    return targets
	return []
	
    def voltmeter_points(self):
	if self.has_voltmeter:
	    V_m = cjson.decode(self.voltmeter_json)['V_m']
	    return len(V_m)
	return 0

    def voltmeter_data(self, sender=None):
	if self.has_voltmeter:
	    def prep_to_vis(status, values):  
		return {'status':status, 'values': values.tolist()}
		
	    V_m = cjson.decode(self.voltmeter_json)['V_m']
	    times = np.arange(1.0, self.network.duration, self.voltmeter_interval())
	    targets = self.voltmeter_targets(data=False)
	    V_m = np.reshape(np.array(V_m), [self.network.duration-1, len(targets)]).T
	    
	    target_list = [target for target in self.network.device_list() if int(target[0]['id']) in targets]
	    if sender in targets:
		V_m = [V_m[targets.index(sender)]]
		target_list = [target_list[targets.index(sender)]]
	    return {'V_m': map(prep_to_vis, target_list, V_m), 'times':times.tolist()}
	return {}
	
    def spike_detector_points(self):
	if self.has_spike_detector:
	    return len(cjson.decode(self.spike_detector_json)['times'])
	return 0
	
    def spike_detector_data(self):
	if self.has_spike_detector:
	    return cjson.decode(self.spike_detector_json)
	return []