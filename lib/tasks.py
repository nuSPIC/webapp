from celery.contrib.abortable import AbortableTask

from reversion import revision
from reversion.models import Version

from network.models import Network
from result.models import Result

import cjson
import datetime

class Simulation(AbortableTask):
    """
    Abortable task to execute NEST.
    
    It needs ID of Network: 
    e.g. Simulation.delay(network_id=5)
    
    For writing in existing results it also needs ID of network version:
    e.g. Simulation.delay(network_id=5, version_id=16)
    
    Producers may invoke the abort() method to request abortion.
    Consumers (workers) periodically checks the is_aborted() method
    at controlled points in their tasks run() method.
    
    """

    def run(self, *args, **kwargs):
	logger = self.get_logger(**kwargs)
	
        network_id = kwargs['network_id']
        network_obj = Network.objects.get(pk=network_id)

        import nest
        nest.ResetKernel()
 
        # Set default for voltmeter
        nest.SetDefaults('voltmeter', {'withgid':False, 'withtime':False})
        
        # Set root status of network
        # TODO it should return failed instead of success
        root_status = network_obj.root_status()
        
        if 'seed' in root_status:
	    seed = int(root_status.pop('seed'))
	    nest.SetStatus([0], {'grng_seed': seed, 'rng_seeds':[seed]})
        
        if root_status:
	    try:
		nest.SetStatus([0], root_status)
	    except:
		logger.warning("Task failed due to setting root status.")
		return
        
        
        # Create models in NEST and set its status
        device_list = network_obj.device_list('all')
        for dev_model, dev_status, dev_params in device_list:
            """ creating models """
            if dev_status:
                params = {}
                for param_key, param_value in dev_status.items():
		    if param_value:
			if ',' in param_value:
			    param_list = param_value.split(',')
			    params[str(param_key)] = param_list
			else:
			    params[str(param_key)] = float(param_value)
                gid = nest.Create(dev_model['label'], params=params)
            else:
                gid = nest.Create(dev_model['label'])
            if 'id' in dev_model:
		assert gid == [int(dev_model['id'])]
    
        # Make connections in nest
        connections = network_obj.connections('all', data=True)
        for source, target, params in connections:
            if params:
                nest.Connect([source],[target], params=params)
            else:
                nest.Connect([source],[target])
                    
        # In case duration is more than 5s, Start simulation for a partial time
        # and checks, if producer is aborted, else simulation goes on.
        duration = network_obj.duration
        if duration > 5000.0:
	    dt = duration/20
            for t in xrange(0, duration, dt):
                if self.is_aborted(**kwargs):
                    # Respect the aborted status and terminate gracefully
                    logger.warning("Task aborted.")
                    return 
                nest.Simulate(dt)
        else:
            nest.Simulate(duration)

	# Get data from output devices
        data = {}
        outputs = network_obj.device_list(modeltype='output')
        for model, dev_status, connections in outputs:
	    gid = [int(model['id'])]
	    output_status = nest.GetStatus(gid)[0]['events']
	    events = {}
	    for key,value in output_status.items():
		events[key] = value.tolist()
	    data[model['label']] = events
            
            
        # Get result object in latest version or in selected version
        if 'version_id' in kwargs:
            version_id = kwargs['version_id']
            version = Version.objects.get(pk=version_id)
            result = version.revision.result
        else:
            version = Version.objects.get_for_object(network_obj).reverse()[0]
            result = version.revision.result
        
        # Write results and simulating date in database and reconfigure the existence of output devices
        result.has_spike_detector, result.has_voltmeter = False, False
        for label, value in data.items():
	    data_json = cjson.encode(value)
	    result.__setattr__("%s_json" %label, data_json)
	    result.__setattr__("has_%s" %label, True)
        result.date_simulated = datetime.datetime.now()
        
        # Save result object
        result.save()
        version_id = result.revision.version_set.latest('revision').pk
        return {'version_id': version_id}