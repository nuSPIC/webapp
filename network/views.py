# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from celery.contrib.abortable import AbortableAsyncResult
from reversion.models import Version

from lib.decorators import render_to
from lib.delivery import networkx
from lib.helpers import get_flatpage_or_none
from lib.tasks import Simulation
import lib.json as json

from network.helpers import values_extend, id_escape, id_identify, dict_to_JSON, csv_to_dict
from network.forms import *
from network.models import SPIC, Network
from network.network_settings import ALL_PARAMS_ORDER

from result.models import Result

import numpy as np
import os
import re
import time

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


@render_to('network_list.html')
def network_list(request):
    """ Get a list of network from architect (unchanged networks). """    
    flatpage = get_flatpage_or_none(request)
    network_list = Network.objects.filter(user_id=0)

    return {
        'flatpage': flatpage,
        'network_list': network_list,
    }   

@login_required
def network_initial(request, SPIC_group, SPIC_id):
    SPIC_obj = get_object_or_404(SPIC, group=SPIC_group, local_id=SPIC_id)
    network_obj, created = Network.objects.get_or_create(user_id=request.user.pk, SPIC=SPIC_obj, local_id=0, deleted=False)
    
    if created:
        # Check if prototype exists
        prototype = get_object_or_404(Network, user_id=0, SPIC=SPIC_obj)
        network_obj.devices_json = prototype.devices_json
        network_obj.save()

    return network(request, SPIC_group, SPIC_id, 0)


def network_latest(request, SPIC_group, SPIC_id, local_id=0):

    network_list = Network.objects.filter(user_id=request.user.id, SPIC__group=SPIC_group, SPIC__local_id=SPIC_id, deleted=False)
    if network_list:
        network_obj = network_list.latest('id')
        local_id = network_obj.local_id

    return network(request, SPIC_group, SPIC_id, local_id)


@render_to('network_split.html')
@login_required
def network_split(request, SPIC_group, SPIC_id):
    SPIC_obj = get_object_or_404(SPIC, group=SPIC_group, local_id=SPIC_id)
    
    left_local_id = request.GET.get('left')
    if not left_local_id:
        left_local_id = '0'
        
    right_local_id = request.GET.get('right')
    if not right_local_id:
        right_local_id = 0  
    
    response = {
        'SPIC_obj': SPIC_obj,
        'left_local_id': left_local_id,
        'right_local_id': right_local_id,
    }
    
    return response   


   
@render_to('network_layout_popup.html')
@login_required
def network_layout(request, SPIC_group, SPIC_id, local_id):
    network_obj = get_object_or_404(Network, user_id=request.user.pk, SPIC__group=SPIC_group, SPIC__local_id=SPIC_id, local_id=local_id)
    
    response = {
        'network_obj': network_obj,
    }
    
    return response


@render_to('network_mini.html')
@login_required
def network_mini(request, SPIC_group, SPIC_id, local_id):

    SPIC_obj = SPIC.objects.get(group=SPIC_group, local_id=SPIC_id)
    network_list = Network.objects.raw('SELECT id,local_id,label,date_simulated,has_voltmeter,has_spike_detector FROM network_network WHERE user_id = %s AND SPIC_id = %s AND deleted = 0', [request.user.pk, SPIC_obj.pk])

    while True:
        try:
            network_obj = Network.objects.get(user_id=request.user.pk, SPIC=SPIC_obj, local_id=local_id, deleted=False)
            break
        except:
            local_id = int(local_id) - 1

    # If request is POST, then it executes any deletions
    if request.method == "POST":

        # Delete selected devices from database.
        if request.POST.get('result_ids'):
            result_ids = request.POST.getlist('result_ids')
            action = request.POST.get('action')
            for result_id in result_ids:
                result = Result.objects.get(pk=int(result_id))
                    
                if action == 'delete':
                    result.delete()
                    result_obj = None
                        
                elif action == 'favorite':
                    result.favorite = True
                    result.save()
                elif action == 'unfavorite':
                    result.favorite = False
                    result.save()
        
        # Delete selected device 
        elif request.POST.get('device_ids'):
            
            device_ids = np.array(request.POST.getlist('device_ids'), dtype=int)
            del_vids = device_ids.copy()

            statusDict = network_obj.device_dict()
            id_filterbank = network_obj.id_filterbank()
            deviceList = network_obj.device_list()

            for device in deviceList:
                if device['type'] == 'input' or device['type'] == 'output':
                    if 'targets' in device:
                        term = 'targets'
                    elif 'sources' in device:        
                        term = 'sources'
                        
                    neuronList = np.array(device[term].split(','), dtype=int)
                    del_term = True
                    for neuron in neuronList:
                        if not neuron in device_ids:
                            del_term = False
                            
                    if del_term:
                        del_vids = np.append(del_vids, device['id'])

            id_updater = np.zeros(len(deviceList))
            id_updater[del_vids-1] = 1
            
            id_updatebank = network_obj.device_list(key='id')
            id_updatebank = np.array([id_updatebank, id_updatebank]).T
            id_updatebank[:,1] -= id_updater.cumsum()

            for device in deviceList:
               
                if not device['id'] in del_vids:
                    # correct device IDs
                    old_id = device['id']
                    tid = id_identify(id_filterbank, old_id)                
                    device['id'] = int(id_escape(id_updatebank, old_id))

                    # delete target/source
                    new_conns = {}
                    if 'targets' in device or 'sources' in device:
                        if 'targets' in device:
                            term = 'targets'
                        elif 'sources' in device:        
                            term = 'sources'
                            
                        value_list = device[term].split(',')
                        value_array = np.array([item for item in enumerate(value_list) if int(item[1]) not in del_vids], dtype=int)
                        
                        if value_array.any():
                            value_list = [str(id_escape(id_updatebank, val)) for val in value_array[:,1]]
                            device[term] = ','.join(value_list)
                        
                            # delete weight and delay
                            if 'weight' in device:
                                weight_list = device['weight'].split(',')
                                weight_list = [str(item[1]) for item in enumerate(weight_list) if item[0] in value_array[:,0]]
                                if not weight_list == ['']:
                                    device['weight'] = ','.join(weight_list)
                                
                            if 'delay' in device:
                                delay_list = device['delay'].split(',')
                                delay_list = [str(item[1]) for item in enumerate(delay_list) if item[0] in value_array[:,0]]
                                if not delay_list == ['']:
                                    device['delay'] = ','.join(delay_list)
                            
                    # merge all status
                    statusDict[('%4d' %tid).replace(' ','0')] = device
                    
            # remove selected device from dict
            new_statusDict = {}
            for old_vid, new_vid in id_updatebank:
                if new_vid > 0 and old_vid not in del_vids:
                    new_statusDict[('%4d' %id_identify(id_filterbank, new_vid)).replace(' ','0')] = statusDict[('%4d' %id_identify(id_filterbank, old_vid)).replace(' ','0')]
                    
            hidden_device_tids = id_identify(id_filterbank, -1)
            for hidden_device_tid in hidden_device_tids:
                new_statusDict[('%4d' %hidden_device_tid).replace(' ','0')] = statusDict[('%4d' %hidden_device_tid).replace(' ','0')]
                
            network_obj.devices_json = json.encode(new_statusDict)
            network_obj.save()
            
        elif request.POST.get('csv'):
            csv = request.POST['csv']
            deviceList = csv_to_dict(csv)
            network_obj.update(deviceList)
            network_obj.save()
       
    label_form = NetworkLabelForm(instance=network_obj)
        
    # Get CSV for expert.
    device_csv_form = DeviceCSVForm({'csv':network_obj.csv()})    
        
    # Get a choice list for adding new device.
    device_choices = []
    outputs = network_obj.outputs()
    for id_model, forms in FORMS.items():
        if not id_model in outputs:
            # get modeltype of device.
            if 'generator' in id_model:
                device_choices.append({'id_model':id_model, 'forms':forms, 'model_type':'input'})
            elif 'meter' in id_model or 'detector' in id_model:
                device_choices.append({'id_model':id_model, 'forms':forms, 'model_type':'output'})
            else:
                device_choices.append({'id_model':id_model, 'forms':forms, 'model_type':'neuron'})
            device_choices.sort(key=lambda x:x['model_type'])
    
            
    # If SPIC1, then pop out neurons from choice list
    if network_obj.SPIC.group == "1":
        device_choices = [device for device in device_choices if device['model_type'] != 'neuron']
        
    
    # Get a list of forms for all devices.
    device_formsets = []
    for id_model, form in FORMS.items():
        device_form = form(network_obj=network_obj)
        formsHTML = render_to_string('device_form.html', {'id_model':id_model, 'form':device_form})
        device_formsets.append({'id_model':id_model, 'formsHTML':formsHTML})
        
    # Get root status
    root_status = network_obj.root_status()
    if 'rng_seeds' in root_status or 'grng_seed' in root_status:
        if root_status['rng_seeds'] == [1] or root_status['grng_seed'] == 1:
            network_form = NetworkForm(instance=network_obj, initial={'same_seed': True})
        else:
            network_form = NetworkForm(instance=network_obj, initial={'same_seed': False})
    else:
        network_form = NetworkForm(instance=network_obj, initial={'same_seed': True})
    
       
    # Prepare for template
    response = {
        'SPIC_obj': SPIC_obj,
        'network_list': network_list,
        'network_obj': network_obj,
        'label_form': label_form,
        'device_csv_form': device_csv_form,
        'network_form': network_form,
        'device_choices': device_choices,
        'device_formsets': device_formsets,
        'params_order': ALL_PARAMS_ORDER,
        'mini': 'mini/',
    }
        
    return response


@render_to('network_mainpage.html')
@login_required
def network(request, SPIC_group, SPIC_id, local_id):
  
    # get objects from database
    SPIC_obj = SPIC.objects.get(group=SPIC_group, local_id=SPIC_id)
    network_list = Network.objects.raw('SELECT id,local_id,label,date_simulated,has_voltmeter,has_spike_detector FROM network_network WHERE user_id = %s AND SPIC_id = %s AND deleted = 0', [request.user.pk, SPIC_obj.pk])
    network_obj = get_object_or_404(Network, user_id=request.user.pk, SPIC=SPIC_obj, local_id=local_id, deleted=False)

    # if request is POST, then it executes any deletions
    if request.method == "POST":
              
        # delete selected network and its result from database.
        if request.POST.get('network_ids'):
            network_ids = request.POST.getlist('network_ids')
            action = request.POST.get('action')
            for network_id in network_ids:
                network = Network.objects.get(pk=int(network_id))
                
                if network.local_id > 0:
                    if action == 'delete':
                        network.deleted = True  
                    elif action == 'favorite':
                        network.favorite = True
                    elif action == 'unfavorite':
                        network.favorite = False
                        
                    network.save()
        
        # delete selected device 
        elif request.POST.get('device_ids'):
            
            device_ids = np.array(request.POST.getlist('device_ids'), dtype=int)
            del_vids = device_ids.copy()

            statusDict = network_obj.device_dict()
            id_filterbank = network_obj.id_filterbank()
            deviceList = network_obj.device_list()

            for device in deviceList:
                if device['type'] == 'input' or device['type'] == 'output':
                    if 'targets' in device:
                        term = 'targets'
                    elif 'sources' in device:        
                        term = 'sources'
                        
                    neuronList = np.array(device[term].split(','), dtype=int)
                    del_term = True
                    for neuron in neuronList:
                        if not neuron in device_ids:
                            del_term = False
                            
                    if del_term:
                        del_vids = np.append(del_vids, device['id'])

            id_updater = np.zeros(len(deviceList))
            id_updater[del_vids-1] = 1
            
            id_updatebank = network_obj.device_list(key='id')
            id_updatebank = np.array([id_updatebank, id_updatebank]).T
            id_updatebank[:,1] -= id_updater.cumsum()

            for device in deviceList:
               
                if not device['id'] in del_vids:
                    # correct device IDs
                    old_id = device['id']
                    tid = id_identify(id_filterbank, old_id)                
                    device['id'] = int(id_escape(id_updatebank, old_id))

                    # delete target/source
                    new_conns = {}
                    if 'targets' in device or 'sources' in device:
                        if 'targets' in device:
                            term = 'targets'
                        elif 'sources' in device:        
                            term = 'sources'
                            
                        value_list = device[term].split(',')
                        value_array = np.array([item for item in enumerate(value_list) if int(item[1]) not in del_vids], dtype=int)
                        
                        if value_array.any():
                            value_list = [str(id_escape(id_updatebank, val)) for val in value_array[:,1]]
                            device[term] = ','.join(value_list)
                        
                            # delete weight and delay
                            if 'weight' in device:
                                weight_list = device['weight'].split(',')
                                weight_list = [str(item[1]) for item in enumerate(weight_list) if item[0] in value_array[:,0]]
                                if not weight_list == ['']:
                                    device['weight'] = ','.join(weight_list)
                                
                            if 'delay' in device:
                                delay_list = device['delay'].split(',')
                                delay_list = [str(item[1]) for item in enumerate(delay_list) if item[0] in value_array[:,0]]
                                if not delay_list == ['']:
                                    device['delay'] = ','.join(delay_list)
                            
                    # merge all status
                    statusDict[('%4d' %tid).replace(' ','0')] = device
                    
            # remove selected device from dict
            new_statusDict = {}
            for old_vid, new_vid in id_updatebank:
                if new_vid > 0 and old_vid not in del_vids:
                    new_statusDict[('%4d' %id_identify(id_filterbank, new_vid)).replace(' ','0')] = statusDict[('%4d' %id_identify(id_filterbank, old_vid)).replace(' ','0')]
                    
            hidden_device_tids = id_identify(id_filterbank, -1)
            for hidden_device_tid in hidden_device_tids:
                new_statusDict[('%4d' %hidden_device_tid).replace(' ','0')] = statusDict[('%4d' %hidden_device_tid).replace(' ','0')]
                
            network_obj.devices_json = json.encode(new_statusDict)
            network_obj.save()
            
        elif request.POST.get('csv'):
            csv = request.POST['csv']
            deviceList = csv_to_dict(csv)
            network_obj.update(deviceList)
            network_obj.save()
            
        
    # Get CSV for expert.
    device_csv_form = DeviceCSVForm({'csv':network_obj.csv()})    
        
    # Get a choice list for adding new device.
    device_choices = []
    outputs = network_obj.outputs()
    for id_model, forms in FORMS.items():
        if not id_model in outputs:
            # get modeltype of device.
            if 'generator' in id_model:
                device_choices.append({'id_model':id_model, 'forms':forms, 'model_type':'input'})
            elif 'meter' in id_model or 'detector' in id_model:
                device_choices.append({'id_model':id_model, 'forms':forms, 'model_type':'output'})
            else:
                device_choices.append({'id_model':id_model, 'forms':forms, 'model_type':'neuron'})
            device_choices.sort(key=lambda x:x['model_type'])
    
            
    # If SPIC1, then pop out neurons from choice list
    if network_obj.SPIC.group == "1":
        device_choices = [device for device in device_choices if device['model_type'] != 'neuron']
        
    
    # Get a list of forms for all devices.
    device_formsets = []
    for id_model, form in FORMS.items():
        device_form = form(network_obj=network_obj)
        formsHTML = render_to_string('device_form.html', {'id_model':id_model, 'form':device_form})
        device_formsets.append({'id_model':id_model, 'formsHTML':formsHTML})
        

        
        
    # Get root status
    root_status = network_obj.root_status()
    if 'rng_seeds' in root_status or 'grng_seed' in root_status:
        if root_status['rng_seeds'] == [1] or root_status['grng_seed'] == 1:
            network_form = NetworkForm(instance=network_obj, initial={'same_seed': True})
        else:
            network_form = NetworkForm(instance=network_obj, initial={'same_seed': False})
    else:
        network_form = NetworkForm(instance=network_obj, initial={'same_seed': True})
        
    # Prepare for template
    response = {
        'SPIC_obj': SPIC_obj,
        'network_list': network_list,
        'network_obj': network_obj,
        'device_csv_form': device_csv_form,
        'network_form': network_form,
        'device_choices': device_choices,
        'device_formsets': device_formsets,
        'params_order': ALL_PARAMS_ORDER,
    }
    
    return response

def device_csv(request, network_id):
    """ AJAX: Check POST request for validation without saving it in database. """
    network_obj = get_object_or_404(Network, pk=network_id)
    layoutSize = network_obj.layout_size()

    if request.is_ajax():
        if request.method == 'POST':
            neuron_ids = request.POST.get('neuron_ids')
            valid = 1
            errorsMsg = {}
            devDict = {}
            
            for model_id, valJSON in request.POST.items():
                if model_id not in ['csrfmiddlewaretoken','neuron_ids']:
                    valDict = json.decode(valJSON)
                    valDict['neuron_ids'] = neuron_ids
                    
                    form = FORMS[valDict['model']](network_obj, valDict)

                    if form.is_valid():
                        devDict[('%4d' %int(valDict['id'])).replace(' ', '0')] = form.cleaned_data
                    else:
                        errorsMsg[str(valDict['id'])] = form.errors
                        valid = -1
                    
            if valid:
                network_obj.device_json = json.encode(devDict)
                
            
            response = {'errorsMsg': errorsMsg, 'valid':valid}
            return HttpResponse(json.encode(response), mimetype='application/json')
            
        else:
            
            device_csv_form = DeviceCSVForm({'data': network_obj.csv()})
            return HttpResponse(device_csv_form.as_div())



def device_preview(request, network_id):
    """ AJAX: Check POST request for validation without saving it in database. """
    network_obj = get_object_or_404(Network, pk=network_id)
    
    if request.is_ajax():
        if request.method == 'POST':

            id_model = request.POST.get('model')
            form = FORMS[id_model](network_obj, request.POST)
            
            # check if form is valid.
            if form.is_valid():
                response = {'valid': 1, 'status': form.cleaned_data, 'statusJSON': dict_to_JSON(form.cleaned_data)}
            else:
                responseHTML = render_to_string('device_form.html', {'form':form})
                response = {'valid': -1, 'responseHTML':responseHTML}
        
            return HttpResponse(json.encode(response), mimetype='application/json')
                    
    return HttpResponse()


def device_commit(request, network_id):
    """ AJAX: Extend targets/sources and write devices in database. """
    network_obj = get_object_or_404(Network, pk=network_id)

    if request.is_ajax():
        if request.method == 'POST':

            edgeList = network_obj.connections(modeltype='neuron')
            deviceList = json.decode(str(request.POST['devices_json']))

            network_obj = network_obj.update(deviceList)
            network_obj.save()
            
            # if all neurons are new, create positions for them.
            if edgeList != network_obj.connections(modeltype='neuron'):
                default_layout(request, network_obj.pk)
            return HttpResponse(json.encode({'saved':1, 'local_id':network_obj.local_id}), mimetype='application/json')
            
    return HttpResponse()


def simulate(request, network_id):
    """
    AJAX: If version_id is 0, it creates a new version of network and then simulates.
    If already simulated, it won't resimulate.
    If task_id is in request.GET, then it aborts the simulation task.
    """
    network_obj = get_object_or_404(Network, pk=network_id)

    if request.is_ajax():
        if request.method == 'POST':
            form = NetworkForm(request.POST, instance=network_obj)

            # check if network form is valid.
            if form.is_valid():
                
                # if not same_seed, generate seeds for root_status
                if form.cleaned_data['same_seed']:
                    root_status = {'rng_seeds': [1], 'grng_seed': 1}
                else:
                    rng_seeds, grng_seed = np.random.random_integers(0,1000,2)
                    root_status = {'rng_seeds': [int(rng_seeds)], 'grng_seed': int(grng_seed)}
                network_obj.status_json = json.encode(root_status)
                
                edgeList = network_obj.connections(modeltype='neuron')
                
                # update deviceList to deviceDict
                deviceList = json.decode(str(request.POST['devices_json']))
                network_obj = network_obj.update(deviceList)
                network_obj.save()  
                
                # if all neurons are new, create positions for them.
                if edgeList != network_obj.connections(modeltype='neuron'):
                    default_layout(request, network_obj.pk)
                 
                task = Simulation.delay(network_obj.id)
                    
                response = {'task_id':task.task_id, 'local_id':network_obj.local_id}
                return HttpResponse(json.encode(response), mimetype='application/json')
                    
            else:
              
                responseHTML = render_to_string('network_form.html', {'form': form})
                response = {'responseHTML':responseHTML, 'valid': -1}
                return HttpResponse(json.encode(response), mimetype='application/json')
                
    return HttpResponse()

def abort(request, task_id):

    abortable_async_result = AbortableAsyncResult(task_id)
    abortable_async_result.abort()
                    
    return HttpResponse()

def label_save(request, network_id):
    """ AJAX: Save network layout."""
    network_obj = get_object_or_404(Network, pk=network_id)
    
    if request.is_ajax():
        if request.method == 'POST':
            network_obj.label = request.POST['label']
            network_obj.save()
            
            response = {'label':network_obj.label}
            return HttpResponse(json.encode(response), mimetype='application/json')
            
    return HttpResponse()       
            

def layout_save(request, network_id):
    """ AJAX: Save network layout."""
    network_obj = get_object_or_404(Network, pk=network_id)

    if request.is_ajax():
        if request.method == 'POST':
        
            post = request.POST
            device_list = json.decode(str(post['devices_json']))
            id_filterbank = network_obj.id_filterbank()
            device_dict = network_obj.device_dict()

            for gid, status in enumerate(device_list):
                
                if 'position' in status:
                    tid = id_identify(id_filterbank, status['id'])
                    if tid:
                        device_dict[('%4d' %tid).replace(' ', '0')]['position'] = status['position']
                
            network_obj.devices_json = json.encode(device_dict)
            network_obj.save()
        
        response = {'layoutSize':network_obj.layout_size()}
        return HttpResponse(json.encode(response), mimetype='application/json')

    return HttpResponse()


def default_layout(request, network_id):
    """ AJAX: Set network layout to default."""
    network_obj = get_object_or_404(Network, pk=network_id)
    
    if request.is_ajax():
        edgelist = network_obj.connections(modeltype='neuron')
        pos = networkx(edgelist, layout='circo')

        deviceDict = network_obj.device_dict()
        id_filterbank = network_obj.id_filterbank()
        neuron_id_filterbank = network_obj.neuron_id_filterbank()
        
        for nid, value in pos.iteritems():
            vid = id_identify(neuron_id_filterbank, nid)
            tid = ("%4d" %id_identify(id_filterbank, vid)).replace(" ", "0")
            deviceDict[tid]['position'] = list(value)
        
        devicesJSON = json.encode(deviceDict)
        network_obj.devices_json = devicesJSON
        network_obj.save()
        
        response = {'device_list':network_obj.device_list(), 'layoutSize': network_obj.layout_size()}
        return HttpResponse(json.encode(response), mimetype='application/json')

    return HttpResponse()
    

def data(request, network_id):
    network_obj = get_object_or_404(Network, pk=network_id)
    
    response = {
        'network': network_obj.device_list(),
        'result' : {}
    }
    
    if network_obj.has_voltmeter:
        response['result']['voltmeter'] = json.decode(network_obj.voltmeter_json)
        
    if network_obj.has_spike_detector:
        response['result']['spike_detector'] = json.decode(network_obj.spike_detector_json)
    
    response = HttpResponse(json.encode(response), mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s_%s.json' %(network_obj.date_simulated.date(), network_obj)

    return response


@render_to('voltmeter.html')
def voltmeter(request, network_id):
    """
    Large View of Voltmeter data for selected neuron (sender)
    """
    
    network_obj = get_object_or_404(Network, pk=network_id)
    neuron = int(request.GET.get('neuron'))
    
    voltmeter = network_obj.voltmeter_data(neuron)
    V_m = voltmeter['V_m'][0]
    assert (len(voltmeter['times']) == len(V_m['values']))
    status = V_m['status']

    response = {
        'values': V_m['values'],
        'times': voltmeter['times'],
    }
    
    return {'voltmeter': json.encode(response)}
    
@render_to('voltmeter_thumbnail.html')
def voltmeter_thumbnail(request, network_id):
    """
    Small View of Voltmeter data
    """
    
    network_obj = get_object_or_404(Network, pk=network_id)
    return {'network_obj': network_obj}

@render_to('spike_detector.html')
def spike_detector(request, network_id):
    """
    View of Spike Detector data
    """
    
    network_obj = get_object_or_404(Network, pk=network_id)
    spike_detector = network_obj.spike_detector_data()
    assert len(spike_detector['senders']) == len(spike_detector['times'])

    spike_detector['neurons'] = network_obj._connect_to(model='spike_detector')
    spike_detector['neuronScale'] = [ii+1 for ii,v in enumerate(spike_detector['neurons'])]

    id_filterbank = network_obj.id_filterbank()
    neuron_id_filterbank = network_obj.neuron_id_filterbank(model="spike_detector")
    spike_detector['senders'] = [id_escape(id_filterbank, sender) for sender in spike_detector['senders']]
    spike_detector['senders'] = [id_escape(neuron_id_filterbank, sender) for sender in spike_detector['senders']]
    
    spike_detector['simTime'] = network_obj.duration
    
    if request.GET.get('view') == 'small':
        spike_detector['fig'] = {'width':250, 'height':300, 'w':210, 'h2':50, 'yticks':3}
    else:
        spike_detector['fig'] = {'width':750, 'height':500, 'w':700, 'h2':150, 'yticks':6}
    
    return spike_detector
