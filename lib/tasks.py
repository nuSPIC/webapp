# -*- coding: utf-8 -*-
from celery.contrib.abortable import AbortableTask

from reversion import revision
from reversion.models import Version

import lib.json as json

from network.forms import NetworkForm
from network.models import Network

import datetime
import numpy as np

class Simulation(AbortableTask):
    """
    Abortable task to execute NEST.
    
    It needs ID of Network: 
    e.g. Simulation.delay(network_id=5)
    
    Producers may invoke the abort() method to request abortion.
    Consumers (workers) periodically checks the is_aborted() method
    at controlled points in their tasks run() method.
    
    """

    def run(self, network_id, *args, **kwargs):
        logger = self.get_logger(**kwargs)
        
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
        for statusDict in device_list:

            """ Create models """
            if statusDict:
                device_params = {}
                statusDefaults = nest.GetDefaults(statusDict['model'])
                for statusKey in statusDefaults.keys():
                    statusVal = statusDict.get(statusKey)
                    if statusVal and statusKey not in ['model']:
                        if isinstance(statusDefaults[statusKey],np.ndarray):
                            statusList = statusVal.split(',')
                            device_params[statusKey] = np.array([float(val) for val in statusList if val])
                        elif isinstance(statusDefaults[statusKey],list):
                            statusList = statusVal.split(',')
                            device_params[statusKey] = [float(val) for val in statusList if val]
                        elif isinstance(statusDefaults[statusKey],float):
                            device_params[statusKey] = float(statusVal)
                        elif isinstance(statusDefaults[statusKey],int):
                            device_params[statusKey] = int(statusVal)  
                        else:
                            device_params[statusKey] = statusVal  
                gid = nest.Create(statusDict['model'], params=device_params)
            else:
                gid = nest.Create(statusDict['model'])

            if statusDict['type'] == 'output':
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
        duration = float(network_obj.duration)
        timestep = 5000.
        
        while duration > timestep:
            if self.is_aborted(**kwargs):
                # Respect the aborted status and terminate gracefully
                # TODO it should return failed instead of success
                logger.warning("Task aborted.")
                return None
            nest.Simulate(timestep)
            duration -= timestep

        if duration > 0.:
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


        # Write results and simulating date in database and reconfigure the existence of output devices
        for label, value in data.items():
            data_json = json.encode(value)
            network_obj.__setattr__("%s_json" %label, data_json)
            network_obj.__setattr__("has_%s" %label, True)
        
        # Update network object
        network_obj.date_simulated = datetime.datetime.now()
        network_obj.save()
        
        return {'network_id': network_obj.pk}