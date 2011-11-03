# -*- coding: utf-8 -*-
from celery.contrib.abortable import AbortableTask

from reversion import revision
from reversion.models import Version

import lib.json as json

from network.helpers import revision_create
from network.forms import NetworkForm
from network.models import Network

from result.models import Result

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
        root_status = network_obj.root_status()

        if root_status:
            nest.SetStatus([0], root_status)


        # Create models in NEST and set its status
        device_list = network_obj.device_list('all')
        outputs = []
        for dev_model, dev_status, dev_params in device_list:

            """ Create models """
            if dev_status:
                status_params = {}
                for status_key, status_value in dev_status.iteritems():
                    if status_value:
                        if ',' in status_value:
                            status_values = status_value.split(',')
                            status_values = [float(val) for val in status_values if val]
                            status_params[str(status_key)] = status_values
                        elif status_key == 'spike_times':
                            status_params[str(status_key)] = [float(status_value)]
                        else:
                            status_params[str(status_key)] = float(status_value)
                gid = nest.Create(dev_model['label'], params=status_params)
            else:
                gid = nest.Create(dev_model['label'])

            if dev_model['type'] == 'output':
                outputs.extend(gid)


        # Make connections in nest
        connections = network_obj.connections('all', data=True)
        for source, target, conn_params, conn_model in connections:
            if conn_params:
                if conn_model:
                    nest.Connect([source],[target], params=conn_params, model=conn_model['model'])

                    syn_params = {}
                    for syn_params_key, syn_params_value in conn_model['syn_params'].iteritems():
                        syn_params[syn_params_key] = float(syn_params_value)
                    nest.SetStatus(nest.FindConnections([source], [target]), syn_params)
                else:
                    nest.Connect([source],[target], params=conn_params)
            else:
                nest.Connect([source],[target])


        # In case duration is more than 5s, Start simulation for a partial time
        # and checks, if producer is aborted, else simulation goes on.
        duration = network_obj.duration
        if duration > 5000.0:
            dt = 5000.0
            for t in xrange(0, duration, dt):
                if self.is_aborted(**kwargs):
                    # Respect the aborted status and terminate gracefully
                    # TODO it should return failed instead of success
                    logger.warning("Task aborted.")
                    return None
                nest.Simulate(dt)

            dt_last = duration % dt
            if dt_last:
                nest.Simulate(dt_last)
        else:
            nest.Simulate(duration)

        # Get data from output devices
        data = {}
        for output_gid in outputs:
            output_status = nest.GetStatus([output_gid])[0]
            if 'events' in output_status:
                output_events = output_status['events']
                events = {}
                for key,value in output_events.items():
                    events[key] = value.tolist()
                data[output_status['model']] = events

                
        # Create a version of network
        versions = Version.objects.get_for_object(network_obj).reverse()
        form = kwargs['form']
#        form = NetworkForm(request.POST, instance=network_obj)

#        try:
#            last_local_id = versions[0].revision.result.local_id
#            revision_create(form, result=True, local_id=last_local_id+1)
#        except:
#            revision_create(form, result=True)


        # Get result object in latest version or in selected version
        version_id = kwargs['version_id']
        if int(version_id) > 0:
            version = Version.objects.get(pk=version_id)
        else:
            version = Version.objects.get_for_object(network_obj).reverse()[0]
        result = version.revision.result

        # Write results and simulating date in database and reconfigure the existence of output devices
        result.has_spike_detector, result.has_voltmeter = False, False
        for label, value in data.items():
            data_json = json.encode(value)
            result.__setattr__("%s_json" %label, data_json)
            result.__setattr__("has_%s" %label, True)
        result.date_simulated = datetime.datetime.now()
        
        # Save result object
        result.save()
        return {'result_local_id': result.local_id}