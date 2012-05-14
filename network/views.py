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

from network.helpers import values_extend, id_escape, id_identify, dict_to_JSON, csv_to_dict, delete_devices
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
def network_latest(request, SPIC_group, SPIC_id):
    SPIC_obj = get_object_or_404(SPIC, group=SPIC_group, local_id=SPIC_id)
    network_list = Network.objects.raw('SELECT id,local_id,label,date_simulated,has_voltmeter,has_spike_detector FROM network_network WHERE user_id = %s AND SPIC_id = %s AND deleted = 0 ORDER BY id DESC', [request.user.pk, SPIC_obj.pk])

    if network_list:
        network_obj = network_list[0]
        local_id = network_obj.local_id

        return network(request, SPIC_group, SPIC_id, local_id)
    else:
        return network_initial(request, SPIC_group, SPIC_id)

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

@render_to('network_split.html')
@login_required
def network_split(request, SPIC_group, SPIC_id):
    SPIC_obj = get_object_or_404(SPIC, group=SPIC_group, local_id=SPIC_id)
    
    left_local_id = request.GET.get('left')
    if not left_local_id:
        left_local_id = 0
        
    right_local_id = request.GET.get('right')
    if not right_local_id:
        right_local_id = 0
    
    response = {
        'SPIC_obj': SPIC_obj,
        'left_local_id': left_local_id,
        'right_local_id': right_local_id,
    }
    
    return response   
   
@render_to('network_mini.html')
@login_required
def network_mini(request, SPIC_group, SPIC_id, local_id):

    SPIC_obj = SPIC.objects.get(group=SPIC_group, local_id=SPIC_id)
    network_list = Network.objects.filter(user_id=request.user.pk, SPIC=SPIC_obj).values('id', 'local_id', 'label', 'comment', 'date_simulated', 'favorite').order_by('-id')
    network_obj = get_object_or_404(Network, user_id=request.user.pk, SPIC__group=SPIC_group, SPIC__local_id=SPIC_id, local_id=local_id, deleted=False)

    # If request is POST, then it executes any deletions
    if request.method == "POST":

        # Delete selected devices from database.
        if request.POST.get('network_ids'):
            network_ids = request.POST.getlist('network_ids')
            action = request.POST.get('action')
            
            for network_id in network_ids:
                network = Network.objects.get(pk=int(network_id))
                
                if network.local_id > 0:
                    if action == 'delete_network':
                        network.deleted = True
                    elif action == 'delete_results':
                        network.has_spike_detector = False
                        network.has_voltmeter = False
                        network.date_simulated = None
                    elif action == 'favorite':
                        network.favorite = True
                    elif action == 'unfavorite':
                        network.favorite = False
                    network.save()
                    
            network_obj = get_object_or_404(Network, user_id=request.user.pk, SPIC=SPIC_obj, local_id=local_id, deleted=False)
        
        # Delete selected device 
        elif request.POST.get('device_ids'):
            device_ids = np.array(request.POST.getlist('device_ids'), dtype=int)
            deviceList = delete_devices(network_obj.device_list(), device_ids)
            
        elif request.POST.get('csv'):
            csv = request.POST['csv']
            deviceList = csv_to_dict(csv)
            
        # update device json in network object
        network_obj = network_obj.update(deviceList)
        network_obj.save()
       
    # Get label and CSV form for expert.
    label_form = NetworkLabelForm(instance=network_obj)
    device_csv_form = DeviceCSVForm({'csv':network_obj.csv()})    
        
    # Get a choice list for adding new device.
    device_choices = []
    outputList = network_obj.output_list()
    for id_model, forms in FORMS.items():
        if not id_model in outputList:
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
        'term': 'mini/',
    }
    
    if network_obj.has_spike_detector:
        spike_detector = network_obj.spike_detector_data()
        assert len(spike_detector['senders']) == len(spike_detector['times'])

        spike_detector['neurons'] = network_obj._connect_to(model='spike_detector')

        id_filterbank = network_obj.id_filterbank()
        neuron_id_filterbank = network_obj.neuron_id_filterbank(model="spike_detector")
        spike_detector['senders'] = [id_escape(id_filterbank, sender) for sender in spike_detector['senders']]
        spike_detector['senders'] = [id_escape(neuron_id_filterbank, sender) for sender in spike_detector['senders']]
        
        spike_detector['simTime'] = network_obj.duration
        
        response['spike_detector'] = spike_detector
        
    return response

@render_to('network_mainpage.html')
@login_required
def network(request, SPIC_group, SPIC_id, local_id):
  
    # get objects from database
    SPIC_obj = SPIC.objects.get(group=SPIC_group, local_id=SPIC_id)
    network_list = Network.objects.filter(user_id=request.user.pk, SPIC=SPIC_obj, deleted=False).values('id', 'local_id', 'label', 'date_simulated', 'favorite').order_by('-id')
    #network_list = Network.objects.raw('SELECT id,local_id,label,date_simulated,has_voltmeter,has_spike_detector FROM network_network WHERE user_id = %s AND SPIC_id = %s AND deleted = 0 ORDER BY id DESC', [request.user.pk, SPIC_obj.pk])
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
                    if action == 'delete_network':
                        network.deleted = True
                    elif action == 'delete_results':
                        network.has_spike_detector = False
                        network.has_voltmeter = False
                        network.date_simulated = None
                    elif action == 'favorite':
                        network.favorite = True
                    elif action == 'unfavorite':
                        network.favorite = False
                    network.save()
                    
            network_obj = get_object_or_404(Network, user_id=request.user.pk, SPIC=SPIC_obj, local_id=local_id, deleted=False)
        
        # delete selected devices
        elif request.POST.get('device_ids'):
            device_ids = np.array(request.POST.getlist('device_ids'), dtype=int)
            deviceList = network_obj.device_list()
            deviceList = delete_devices(deviceList, device_ids)
            print deviceList
            
            
        elif request.POST.get('csv'):
            csv = request.POST['csv']
            deviceList = csv_to_dict(csv)

        # update device json in network object
        network_obj = network_obj.update(deviceList)
        network_obj.save()
            
    # Get CSV for expert.
    device_csv_form = DeviceCSVForm({'csv':network_obj.csv()})    
        
    # Get a choice list for adding new device.
    device_choices = []
    outputList = network_obj.output_list()
    for id_model, forms in FORMS.items():
        if not id_model in outputList:
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
        'term': '',
    }
    
    if network_obj.has_spike_detector:
        spike_detector = network_obj.spike_detector_data()
        assert len(spike_detector['senders']) == len(spike_detector['times'])

        spike_detector['neurons'] = network_obj._connect_to(model='spike_detector')

        id_filterbank = network_obj.id_filterbank()
        neuron_id_filterbank = network_obj.neuron_id_filterbank(model="spike_detector")
        spike_detector['senders'] = [id_escape(id_filterbank, sender) for sender in spike_detector['senders']]
        spike_detector['senders'] = [id_escape(neuron_id_filterbank, sender) for sender in spike_detector['senders']]
        
        spike_detector['simTime'] = network_obj.duration
        
        response['spike_detector'] = spike_detector
    
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
                        devDict[str(valDict['id'])] = form.cleaned_data
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
                device_id = form.cleaned_data['id']
                device_ids = network_obj.device_list(key='id')
                if device_id in device_ids:
                    idx = device_ids.index(device_id)
                else:
                    idx = -1
                
                
                response = {'valid': 1, 'idx': idx, 'status': form.cleaned_data, 'statusJSON': dict_to_JSON(form.cleaned_data)}
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
                layout_default(request, network_obj.pk)
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
                edgeList = network_obj.connections(modeltype='neuron')
                
                # update deviceList to deviceDict
                deviceList = json.decode(str(request.POST['devices_json']))
                network_obj = network_obj.update(deviceList)
                
                network_obj.duration = form.cleaned_data['duration']
                # if not same_seed, generate seeds for root_status
                if form.cleaned_data['same_seed']:
                    root_status = {'rng_seeds': [1], 'grng_seed': 1}
                else:
                    rng_seeds, grng_seed = np.random.random_integers(0,1000,2)
                    root_status = {'rng_seeds': [int(rng_seeds)], 'grng_seed': int(grng_seed)}
                network_obj.status_json = json.encode(root_status)

                network_obj.save()
                time.sleep(1)
                
                # if all neurons are new, create positions for them.
                if edgeList != network_obj.connections(modeltype='neuron'):
                    layout_default(request, network_obj.pk)
                    
                task = Simulation.delay(network_obj.pk)
                    
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
            

@render_to('raphael.network_layout_popup.html')
@login_required
def network_layout(request, SPIC_group, SPIC_id, local_id):
    network_obj = get_object_or_404(Network, user_id=request.user.pk, SPIC__group=SPIC_group, SPIC__local_id=SPIC_id, local_id=local_id, deleted=False)
    
    response = {
        'network_obj': network_obj,
    }
    
    return response

def layout_save(request, network_id):
    """ AJAX: Save network layout."""
    network_obj = get_object_or_404(Network, pk=network_id)

    if request.is_ajax():
        if request.method == 'POST':
            deviceList = json.decode(request.POST.get('devices_json'))
            
            network_obj = network_obj.update(deviceList, force_self=True)
            network_obj.save()
        
        response = {'layoutSize':network_obj.layout_size()}
        return HttpResponse(json.encode(response), mimetype='application/json')

    return HttpResponse()

def layout_default(request, network_id):
    """ AJAX: Set network layout to default."""
    network_obj = get_object_or_404(Network, pk=network_id)
    
    if request.is_ajax():
        edgelist = network_obj.connections(modeltype='neuron')
        pos = networkx(edgelist, layout='circo')
        
        deviceList = network_obj.device_list()
        neuron_id_filterbank = network_obj.neuron_id_filterbank()
        
        for idx, device in enumerate(deviceList):
            if device['type'] == 'neuron':
                neuron_idx = id_escape(neuron_id_filterbank, device['id'])
                if neuron_idx in pos:
                    device['position'] = list(pos[neuron_idx])
                    deviceList[idx] = device
        
        network_obj = network_obj.update(deviceList, force_self=True)
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
    response['Content-Disposition'] = 'attachment; filename=%s_%s_%s.json' %(network_obj.date_simulated.strftime('%y%m%d'), network_obj.SPIC, network_obj.local_id)

    return response


@render_to('protovis.voltmeter.html')
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
    
@render_to('protovis.voltmeter_thumbnail.html')
def voltmeter_thumbnail(request, network_id):
    """
    Small View of Voltmeter data
    """
    
    network_obj = get_object_or_404(Network, pk=network_id)
    return {'network_obj': network_obj}

@render_to('d3.spike_detector.html')
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
        spike_detector['fig'] = {'width':300, 'height':300, 'w':300, 'h2':50, 'xticks':5, 'yticks':3}
    else:
        spike_detector['fig'] = {'width':750, 'height':500, 'w':1200, 'h2':500, 'xticks':20, 'yticks':6}
    
    return spike_detector
