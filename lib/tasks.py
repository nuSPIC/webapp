# -*- coding: utf-8 -*-
from celery.contrib.abortable import AbortableTask

#from reversion import revision
#from reversion.models import Version

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
        nodes = network_obj.nodes('all')
        nodes_id = [node['id'] for node in nodes]

        outputs = []
        for node in nodes:
            status = node['status']

            """ Create models """
            if status:
                device_params = {}
                statusDefaults = nest.GetDefaults(status['model'])
                for statusKey in statusDefaults.keys():
                    statusVal = status.get(statusKey)
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
                gid = nest.Create(status['model'], params=device_params)
            else:
                gid = nest.Create(status['model'])

            assert(gid[0] == node['id'])
            if node['type'] == 'output':
                outputs.extend(gid)

        # Make connections in nest
        links = network_obj.links('all', out='object')
        for link in links:
            if 'synapse' in link:
                nest.Connect([link['source']['id']], [link['target']['id']], {'weight': link['weight'], 'delay': link['delay']}, link['synapse']['model'])
                nest.SetStatus(nest.FindConnections([link['source']['id']], [link['target']['id']]), link['synapse']['status'])
            else:
                nest.Connect([link['source']['id']], [link['target']['id']], {'weight': float(link['weight']), 'delay': float(link['delay'])})

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
            if output_status['model'] == 'spike_detector':
                neurons = [nodes[nodes_id.index(sender)] for sender in np.unique(events['senders'])]
                if len(neurons) > 0:
                    network_obj.has_spike_detector = True
            if output_status['model'] == 'voltmeter':
                neurons = [{'uid': link['target']['uid'], 'id': link['target']['id']} for link in links if link['source']['status']['model'] == 'voltmeter']
                if len(neurons) > 0:
                    network_obj.has_voltmeter = True
            data[output_status['model']]['meta'] = {'neurons': neurons}

        # Write results and simulating date in database and reconfigure the existence of output devices
        for label, value in data.items():
            data_json = json.encode(value)
            network_obj.__setattr__("%s_json" %label, data_json)

        # Update network object
        network_obj.date_simulated = datetime.datetime.now()
        network_obj.save()
        
        return {'local_id': network_obj.local_id}
