# -*- coding: utf-8 -*-
import nest
import numpy as np
import pdb
import pylab as pl
import sys

from network.models import Network

nest.ResetKernel()

network_obj = Network.objects.get(pk=int(sys.argv[1]))

# Create models in NEST and set its status
device_list = network_obj.device_list('all')
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

# Make connections in nest

pdb.set_trace()

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




# Manual devices
#spg = nest.Create('spike_generator',1,{'spike_times':[200.,280.,315.,400.]})
#nest.Connect(spg,[1],{'weight':100.})
#vm = nest.Create('voltmeter')
#nest.Connect(vm,[3])
#nest.SetStatus(nest.FindConnections([1]), {'weight':10.})

# In case duration is more than 5s, Start simulation for a partial time
# and checks, if producer is aborted, else simulation goes on.
nest.Simulate(sys.argv[2])

vm = [9]
    
# Plot
pl.clf()
V_m = nest.GetStatus(vm)[0]['events']['V_m']
times = nest.GetStatus(vm)[0]['events']['times']
pl.plot(times, V_m)
pl.show()