from django.contrib.auth.models import User
from django.db import models
from django.utils import simplejson

SPIC_CHOICES = (
	('1','SPIC1'),
	('2','SPIC2'),
	('3','SPIC3'),
	('4','SPIC4')
)

class Network(models.Model):
    user_id = models.IntegerField()
    SPIC_id = models.CharField(max_length=6, choices=SPIC_CHOICES)
    local_network_id = models.IntegerField()
    
    title = models.CharField(null=True, blank=True, max_length=32)
    description = models.TextField(blank=True)    
    
    duration = models.FloatField(null=True, default=500.0)
    status_json = models.TextField(blank=True, verbose_name='Root status')
    seed = models.IntegerField(null=True, default=1)
    devices_json = models.TextField(blank=True, verbose_name='Devices')
    
    def user(self):
	"""
	Gets user object from the django model 'auth' by user_id.
	CAUTION: the model 'auth' might be stored in other database.
	"""
	
	if self.user_id == 0:
	    return 'architect'
	else:
	    return User.objects.get(pk=self.user_id)

    def __unicode__(self):
        return '%s_%s_%s' %(self.user(), self.get_SPIC_id_display(), self.local_network_id)
    
    def device_list(self, modeltype=None):
	"""
	Returns a list of devices by loading JSON from the field devices_json.
	Argument modeltype is for filtering devices by its type,
	its default is None, choices are 'neuron', 'input' or 'output'.
	"""
	
	devices = simplejson.loads(self.devices_json)
	if modeltype:
	    return [dev for dev in devices if dev[1]['type']==modeltype]
	return devices
    
    def last_device_id(self):
	"""
	Returns in case of existing devices the last ID of device 
	as a marker for adding new device. Otherwise it returns None.
	"""
	
	if self.devices_json:
	    return self.device_list()[-1][0]
	return
	
    def voltmeter(self):
	"""
	Returns status data of voltmeter from the field device_json.
	"""
	
	voltmeter = [dev for dev in self.device_list('output') if dev[1]['label'] == 'voltmeter']
	return voltmeter != []
	
    def spike_detector(self):
	"""
	Returns status data of spike detector from the field device_json.
	"""	
	
	spike_detector = [dev for dev in self.device_list('output') if dev[1]['label'] == 'spike_detector']
	return spike_detector != []	
	
    def neuron_ids(self):
	"""
	Gets a list of neuron ID for connectivity matrix and
	validation check of targets/sources.
	"""
	
	return [int(dev[0]) for dev in self.device_list() if dev[1]['type']== 'neuron']
	
    def weight_list(self):
	"""
	Gets a listed tuple of device ID and list of weights for connectivity matrix.
	"""
	
	w_list = []
	for gid, model, status, params in self.device_list():
	    if 'weight' in params:
		weights = []
		try:
		    targets = params['targets'].split(',')
		    targets = [int(tgt) for tgt in targets]
		    weight = params['weight'].split(',')
		except:
		    targets = []
		    
		for neuron_id, neuron_model, neuron_status, neuron_params in self.device_list('neuron'):
		    if neuron_id in targets:
			try:
			    weights.append(u'%s' %weight[targets.index(neuron_id)%len(weight)])
			except:
			    weights.append(u'%s' %weight[0])
		    else:
			weights.append(u' ')
		w_list.append((gid, weights))
	return w_list
	
    def delay_list(self):
	"""
	Gets a listed tuple of device ID and list of delays for connectivity matrix.
	"""
	
	d_list = []
	for gid, model, status, params in self.device_list():
	    if 'delay' in params:
		delays = []
		try:
		    targets = params['targets'].split(',')
		    targets = [int(tgt) for tgt in targets]
		    delay = params['delay'].split(',')
		except:
		    targets = []
		    
		for neuron_id, neuron_model, neuron_status, neuron_params in self.device_list('neuron'):
		    if neuron_id in targets:
			try:
			    delays.append(u'%s' %delay[targets.index(neuron_id)%len(delay)])
			except:
			    delays.append(u'%s' %delay[0])
		    else:
			delays.append(u' ')
		d_list.append((gid, delays))
	return d_list

    def connections(self, data=False, modeltype=None):
	"""
	Gets a listed tuple of source and target in each connection.
	If data is True, it also returns dictionary of weight and delay.
	modeltype default is None, choices are 'neuron', 'input' or 'output'.
	-> see the method device_list.
	"""	
	
	connections = []
	if modeltype == 'IO_device':
	    connections.extend(self.connections(data=data, modeltype='input'))
	    connections.extend(self.connections(data=data, modeltype='output'))
	else:
	    device_list = self.device_list(modeltype)
	    for gid, model, status, params in device_list:
		if params:
		    if model['label'] == u'spike_detector':
			if len(params['sources']) > 0:
			    sources = params['sources'].split(',')
			    for index, source in enumerate(sources):
				if data:
				    connections.append((int(source),gid, None))
				else:
				    connections.append((int(source),gid))
				    
		    else:
			if len(params['targets']) > 0:
			    targets = params['targets'].split(',')
			    for index, target in enumerate(targets):
				if data:
				    weights, delays = params['weight'].split(','), params['delay'].split(',')
				    index_weight, index_delay = index%len(weights), index%len(delays)
				    connection_params = {'weight':float(weights[index_weight]), 'delay':float(delays[index_delay])}
				    connections.append((gid, int(target), connection_params))
				else:
				    connections.append((gid,int(target)))
				    
	return connections
	
    def neurons(self):
	"""
	Returns a readable string of all neurons.
	"""
	
	neuron_list = [(dev[1]['label'], int(dev[0])) for dev in self.device_list('neuron')]
	if len(neuron_list) < 20:
	    return ", ".join(["%s [%s]"%neuron for neuron in neuron_list])
	else:
	    return '%s neurons' %len(neuron_list)

    def	inputs(self):
	"""
	Returns a readable string of all inputs.
	"""
	
	
	return ", ".join(["%s [%s]"%(ii[1]['label'],ii[0]) for ii in self.device_list('input')])
	
    def	outputs(self):
	"""
	Returns a readable string of all outputs.
	"""
	
	return ", ".join(["%s [%s]"%(oo[1]['label'],oo[0]) for oo in self.device_list('output')])