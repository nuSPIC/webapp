# -*- coding: utf-8 -*-
from __future__ import print_function

from network.models import Network, SPIC
from network.forms import *

from result.models import Result
from reversion.models import Version

import lib.json as json
import sys
import pdb

SPIC_LIST = [
	('0','1','Sandbox'), 
	('1','1','Hodgkin-Huxley'), 
	('1','2','Cajal'), 
	('1','3','Hebb'), 
	('1','4','Marr'), 
	('2','1','Braitenbach')
]

# Define models with its modeltype, label and form.
FORMS = {
    #'hh_psc_alpha': HhPscAlphaForm,
    'iaf_cond_alpha': IafCondAlphaForm,
    'iaf_neuron': IafNeuronForm,
    'iaf_psc_alpha': IafPscAlphaForm,
    #'parrot_neuron': ParrotForm,
    
    'ac_generator': ACGeneratorForm,
    'dc_generator': DCGeneratorForm,
    'poisson_generator': PoissonGeneratorForm,
    'noise_generator': NoiseGeneratorForm,
    #'smp_generator': SmpGeneratorForm,
    'spike_generator': SpikeGeneratorForm,   
    
    'spike_detector': SpikeDetectorForm,
    'voltmeter': VoltmeterForm,
    }

"""
Add table network_spic in database:
manage.py syncdb --database=network

Select database,

Add columns in table:
ALTER TABLE network_network ADD COLUMN SPIC_tmp varchar(6);
ALTER TABLE network_network ADD COLUMN label varchar(16);
ALTER TABLE network_network ADD COLUMN date_simulated datetime;
ALTER TABLE network_network ADD COLUMN comment longtext;
ALTER TABLE network_network ADD COLUMN favorite tinyint (1) NOT NULL;
ALTER TABLE network_network ADD COLUMN deleted tinyint (1) NOT NULL;
ALTER TABLE network_network ADD COLUMN has_voltmeter tinyint (1) NOT NULL;
ALTER TABLE network_network ADD COLUMN has_spike_detector tinyint (1) NOT NULL;
ALTER TABLE network_network ADD COLUMN voltmeter_json longtext NOT NULL;
ALTER TABLE network_network ADD COLUMN spike_detector_json longtext NOT NULL;
"""


def versionConverter(user_id=1):
    networkList = Network.objects.filter(user_id=user_id)
    old_ids = []
    
    for network_obj in networkList:
        print('%4d -\t%15s -' %(network_obj.id, network_obj.label), end=" ")
        versionList = Version.objects.get_for_object(network_obj)
        versionList = versionList.order_by('id')
        
        if user_id = 0:
            versionList = [versionList.latest('id')]
        
        network_obj.SPIC_tmp = network_obj.SPIC_id
        network_obj.save()
        
        if versionList:
            print('versions found.')
        else:
            print('no versions.')
        
        local_id = 0
        for version_obj in versionList:

            print('\tversion %4d...' %version_obj.id, end="")

            try:
               result_obj = version_obj.revision.result
            except:
               continue

            kwargs = version_obj.field_dict
            del kwargs['id']
            net = Network(**kwargs)
            
            old_ids.append(network_obj.id)
            
            net.SPIC_tmp = net.SPIC_id
            net.date_simulated = result_obj.date_simulated
            net.comment = result_obj.comment
            net.favorite = result_obj.favorite
            net.has_voltmeter = result_obj.has_voltmeter
            net.voltmeter_json = result_obj.voltmeter_json
            net.has_spike_detector = result_obj.has_spike_detector
            net.spike_detector_json = result_obj.spike_detector_json
          
            print("%s" %net.__dict__)
            print("%s: " %net, end=" ")
            save_entry = raw_input("all correct, save network [Y/n]? ")
            if not save_entry or save_entry == 'y': net.save()

    old_ids = list(set(old_ids))
    
    print('old ids - %s' %old_ids)
    del_entry = raw_input("delete old network [y/N]?")    
    if not del_entry or del_entry == 'n':
        return old_ids
    elif del_entry == 'y':
        for old_id in old_ids:
            old_net = Network.objects.get(id=old_id)
            old_net.delete()

"""
uncomment SPIC and comment SPIC_id fields in model

Select database;

Alter columns in table:
ALTER TABLE network_network CHANGE SPIC_id SPIC_id int, add key ( SPIC_id );
"""

def SPICConverter(user_id=1):
  
    all_networks = []
    for group, local_id, title in SPIC_LIST:
        SPIC_obj,create = SPIC.objects.get_or_create(group=group,local_id=local_id,title=title)
    
        networkList = Network.objects.filter(user_id=user_id, SPIC_tmp=SPIC_obj.group, local_id=SPIC_obj.local_id)

        local_id = 0
        for net in networkList:
            net.SPIC = SPIC_obj
            net.local_id = local_id
            local_id += 1

        if networkList:
            all_networks.extend(networkList)
        
    print('Verify check for %s' %SPIC_obj.get_group_display())
    [print('\t%s: %s == %s ?' %(n.local_id, n.SPIC, n.title)) for n in all_networks]
        
    save_entry = raw_input("all correct, save network [Y/n]? ")
    print('network ids:', end=" ")
    if not save_entry or save_entry == 'y': 
        for net in all_networks:
            net.save()
            print('%s, ' %net.id, end=" ")
        print('...saved.')


"""
Comment fields SPIC_tmp, title, description in network
"""

def jsonConverter(user_id=1, id=None):
    print(20 * '- ')
    print('start converting Device JSON')
    if id:
        networkList = Network.objects.filter(id=id)
    else:
        networkList = Network.objects.filter(user_id=user_id)
    for network_obj in networkList:
        devicesJSON = network_obj.devices_json
        if devicesJSON:
                print('%4d - %30s' %(network_obj.pk, network_obj),end="")
                devicesDict = json.decode(devicesJSON)
                neuron_ids = network_obj.neuron_ids()

                for tid, status in devicesDict.items():
                    if len(status) == 3:
                        status[0].update(status[1])
                        status[0].update(status[2])
                        status = status[0]

                    if not status.get('model'):
                        status['model'] = status.get('label')
                    elif not status.get('label'):
                        status['label'] = status.get('model')

                    if status['model'] in FORMS:
                        status['neuron_ids'] = neuron_ids
                        form = FORMS[status['model']](network_obj, status)

                        if form.is_valid():
                            for k, v in form.cleaned_data.items():
                                if v:
                                    status[k] = v
                                elif k in status:
                                    del status[k]
                                
                        if 'neuron_ids' in status:
                            del status['neuron_ids']
                    print('.', end="")
                    devicesDict[tid] = status
                    
                network_obj.devices_json = json.encode(devicesDict)
                network_obj.save()
                print('successfully saved.')
                
                
def updateInitial():
    architect_networks = Network.objects.filter(user_id=0)
    
    for arch_net in architect_networks:
        all_networks = Network.objects.filter(SPIC=arch_net.SPIC, local_id=0)
        
        for net in all_networks:
            net.status_json = arch_net.status_json
            net.devices_json = arch_net.devices_json
            net.duration = arch_net.duration
            
            net.save()