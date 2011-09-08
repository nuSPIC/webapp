# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from celery.contrib.abortable import AbortableAsyncResult
from reversion.models import Version
from reversion import revision

from lib.decorators import render_to
from lib.delivery import networkx
from lib.tasks import Simulation
from lib.helpers import get_flatpage_or_none

from network.models import Network
from network.helpers import values_extend
from network.forms import *

from result.models import Result
from result.forms import CommentForm

import os
import cjson

# Define models with its modeltype, label and form.
MODELS = [
    {'model_type': 'neuron',         'id_label': 'hh_psc_alpha',         'form': HhPscAlphaForm,},
    {'model_type': 'neuron',         'id_label': 'iaf_cond_alpha',         'form': IafCondAlphaForm,},
    {'model_type': 'neuron',         'id_label': 'iaf_neuron',                 'form': IafNeuronForm,},
    {'model_type': 'neuron',         'id_label': 'iaf_psc_alpha',         'form': IafPscAlphaForm,},
    
    {'model_type': 'input',         'id_label': 'ac_generator',         'form': ACGeneratorForm,},
    {'model_type': 'input',         'id_label': 'dc_generator',                'form': DCGeneratorForm,},
    {'model_type': 'input',         'id_label': 'poisson_generator','form': PoissonGeneratorForm,},
    {'model_type': 'input',         'id_label': 'noise_generator',         'form': NoiseGeneratorForm,},
    {'model_type': 'input',         'id_label': 'smp_generator',         'form': SmpGeneratorForm,},
   # {'model_type': 'input',         'id_label': 'spike_generator',         'form': SpikeGeneratorForm,},   
    
    {'model_type': 'output',         'id_label': 'spike_detector',         'form': SpikeDetectorForm,},
    {'model_type': 'output',         'id_label': 'voltmeter',                 'form': VoltmeterForm,},
]

@revision.create_on_success
def revision_create(obj, result=False, **kwargs):
    """ Create a revision for network object. """
    obj.save()
    if result:
        revision.add_meta(Result, **kwargs)

@render_to('network_list.html')
def network_list(request):
    """ Get a list of network from architect (unchanged networks). """    
    flatpage = get_flatpage_or_none(request)
    network_list = Network.objects.filter(user_id=0)
    
    return {
        'flatpage': flatpage,
        'network_list': network_list,
    }        

@render_to('network.html')
@login_required
def network(request, SPIC_id, local_id):
    return network_simulated(request, SPIC_id, local_id, -1)
    
@render_to('network.html')
@login_required
def network_simulated(request, SPIC_id, local_id, result_id):
    """ Main view for network workplace """
    
    # Check if prototype exists
    prototype = get_object_or_404(Network, user_id=0, SPIC_id=SPIC_id, local_id=local_id)

    # If network is created, then it create a copy from prototype and an initial version of network.
    network_obj, created = Network.objects.get_or_create(user_id=request.user.pk, SPIC_id=SPIC_id, local_id=local_id)
    if created:
        network_obj.title = prototype.title
        network_obj.description = prototype.description
        network_obj.devices_json = prototype.devices_json
        revision_create(network_obj)
    
    result_obj = None
    version_id = 0
    
    # Get a list of network versions in reverse date is created.
    versions = Version.objects.get_for_object(network_obj)
    
    if int(result_id) == 0:
        result_id = -1
    elif int(result_id) > 0:
        try:
            results = [version.revision.result for version in versions[1:]]
            result_ids = [result.local_id for result in results]
            result_id = result_ids.index(int(result_id))
            result_obj = results[result_id]
            version_id = versions[result_id +1].pk
        except:
            pass
        
    if request.GET.get('version'):
        version = versions[result_id +1].revision.revert()
        network_obj = Network.objects.get(user_id=request.user.pk, SPIC_id=SPIC_id, local_id=local_id)   

    
    # If request is POST, then it executes any deletions
    if request.method == "POST":
        
        # Delete selected devices from database.
        if request.POST.get('version_ids'):
            version_ids = request.POST.getlist('version_ids')
            action = request.POST.get('action')
            for vid in version_ids:
                version_edit = Version.objects.get(pk=int(vid))
                result = version_edit.revision.result
                if action == 'delete':
                    version_edit.delete()
                    result.delete()
                    result_obj = None
                elif action == 'favorite':
                    result.favorite = True
                    result.save()
                elif action == 'unfavorite':
                    result.favorite = False
                    result.save()
        
        # Delete selected versions of history.
        elif request.POST.get('device_ids'):
            device_ids = [int(device_id) for device_id in request.POST.getlist('device_ids')]
            device_list = [dev for dev in network_obj.device_list() if not int(dev[0]['id']) in device_ids]
            
            # get new device IDs and update
            new_device_ids = {}
            for index, device in enumerate(device_list):
                if not index == int(device[0]['id']):
                    new_device_ids[device[0]['id']] = index + 1
                    device[0]['id'] = index + 1
            
            # correct device IDs and targets/sources
            for idx, device in enumerate(device_list):

                if device[2] == {}:
                    if 'targets' in device[2]:
                        key = 'targets'
                    elif 'sources' in device[2]:        
                        key = 'sources'
                        
                    value_list = device[2][key].split(',')
                    values_index = [index for index, val in enumerate(value_list) if int(val) in device_ids]
                    
                    # delete old target/source
                    value_list = [val for index, val in enumerate(value_list) if index not in values_index]
                    
                    # correct targets/sources
                    value_list = [str(new_device_ids[val]) for val in value_list]
                    values = ','.join(value_list)
                    params = {key:values}
                    
                    # delete weight and delay
                    if 'weight' in device[2]:
                        weight_list = device[2]['weight'].split(',')
                        weight_list = [val for index, val in enumerate(weight_list) if index not in values_index]
                        params['weight'] = ','.join(weight_list)
                        
                    if 'delay' in device[2]:
                        delay_list = device[2]['delay'].split(',')
                        delay_list = [val for index, val in enumerate(delay_list) if index not in values_index]
                        params['delay'] = ','.join(delay_list)
                    
                    # merge all status
                    device_list[idx] = device[0], device[1], params
            
            hidden_device_list = network_obj.device_list('hidden')
            network_obj.devices_json = cjson.encode(device_list+hidden_device_list)
            network_obj.save()
            
    # Get a choice list for adding new device.
    if network_obj.devices_json:
        device_choices = []
        outputs = network_obj.outputs()
        for device in MODELS:
            if not device['id_label'] in outputs:
                device_choices.append(device)
    else:
        device_choices = MODELS
            
    # If SPIC1, then pop out neurons from choice list
    if network_obj.SPIC_id == "1":
        device_choices = [device for device in device_choices if device['model_type'] != 'neuron']
    
    # Get a list of forms for all devices.
    device_formsets = []
    for device in MODELS:
        device_form = device['form'](network_obj=network_obj)
        formsHTML = render_to_string('device_form.html', {'id_label':device['id_label'], 'form':device_form})
        device_formsets.append({'id_label':device['id_label'], 'formsHTML':formsHTML})
        

    # If result exist, then get form for comment.
    if result_obj:
        comment_form = CommentForm(instance=result_obj)
    else:
        comment_Form = None
        
    response = {
        'network_obj': network_obj,
        'network_form': NetworkForm(instance=network_obj),
        'device_choices': device_choices,
        'device_formsets': device_formsets,
        'versions': versions.reverse(),
        'version_id': version_id,
    }
        
    if result_obj:
        response['result_obj'] = result_obj
        response['comment_form'] = comment_form
        
    return response

def device_preview(request, network_id):
    """ AJAX: Check POST request for validation without saving it in database. """

    network_obj = get_object_or_404(Network, pk=network_id)
    if request.is_ajax():
        if request.method == 'POST':
            id_label = request.POST.get('model')
            id_labels = [device['id_label'] for device in MODELS]
            device = MODELS[id_labels.index(id_label)]
            form = device['form'](network_obj, request.POST)
            
            # check if form is valid.
            if form.is_valid():
                data = form.data.copy()
                data.pop('csrfmiddlewaretoken')
                label = data.pop('model')[0]
                
                # get modeltype of device.
                if 'generator' in label:
                    modeltype = 'input'
                elif 'meter' in label or 'detector' in label:
                    modeltype = 'output'
                else:
                    modeltype = 'neuron'
                model = {'id': None, 'label':label, 'type':modeltype}
                
                # get sources or targets.
                if 'targets' in data:
                    term = 'targets'
                elif 'sources' in data:
                    term = 'sources'
                    
                # it doesn't save weight and delay, if they don't exist.                    
                if 'weight' in data and 'delay' in data:
                    params = {term: data.pop(term)[0], 'weight': data.pop('weight')[0], 'delay': data.pop('delay')[0]}
                else:
                    params = {term: data.pop(term)[0]}
                status = {}
                
                # save status of each divices.
                for key, value in data.items():
                    status[key] = value
                    
                response = {'valid': 1, 'device':[model, status, params]}
                
            else:
                response = {'valid': -1, 'id_label':id_label}
        
            responseHTML = render_to_string('device_form.html', {'id_label':device['id_label'], 'form':form})
            response['responseHTML'] = responseHTML
            return HttpResponse(cjson.encode(response), mimetype='application/json')
                    
    return HttpResponse()

def device_commit(request, network_id):
    """ AJAX: Extend targets/sources and write devices in database. """
    
    network_obj = get_object_or_404(Network, pk=network_id)
    if request.is_ajax():
        if request.method == 'POST':
            post = request.POST
            device_list = cjson.decode(post['devices_json'])
        
            for gid, device in enumerate(device_list):
                model, status, params = device
                if 'targets' in params or 'sources' in params:
                    if 'targets' in params:
                        term = 'targets'
                    else:
                        term = 'sources'
                    try:
                        extended_list = values_extend(params[term], unique=True, toString=True)
                    except:
                        extended_list = []

                    device_list[gid][2][term] = ','.join(extended_list)
                
            hidden_device_list = network_obj.device_list('hidden')
            network_obj.devices_json = cjson.encode(device_list + hidden_device_list)
            network_obj.save()
            return HttpResponse(cjson.encode({'saved':1}), mimetype='application/json')
            
    return HttpResponse()

def simulate(request, network_id, version_id):
    """
    AJAX: If version_id is 0, it creates a new version of network and then simulates.
    If already simulated, it won't resimulate.
    If task_id is in request.GET, then it aborts the simulation task.
    """
    
    network_obj = get_object_or_404(Network, pk=network_id)
    if request.is_ajax():
        if request.method == 'POST':
            post = request.POST
            device_list = cjson.decode(post['devices_json'])
            
            for gid, device in enumerate(device_list):
                model, status, params = device
                
                cleaned_status = {}
                for status_key, status_value in status.iteritems():
                    if status_value:
                        cleaned_status[status_key] = status_value
                device_list[gid][1] = cleaned_status
                
                if 'targets' in params or 'sources' in params:
                    if 'targets' in params:
                        term = 'targets'
                    else:
                        term = 'sources'
                    try:
                        extended_list = values_extend(params[term], unique=True, toString=True)
                    except:
                        extended_list = []

                    device_list[gid][2][term] = ','.join(extended_list)
            
            hidden_device_list = network_obj.device_list('hidden')
            network_obj.devices_json = cjson.encode(device_list + hidden_device_list)
            form = NetworkForm(request.POST, instance=network_obj)
            
            versions = Version.objects.get_for_object(network_obj).reverse()

            # check if network form is valid.
            if form.is_valid():
                
                # if network form is changed or version_id is 0, a new version will be created. 
                # Otherwise it simulates without creating new version.
                if form.has_changed() or int(version_id) == 0:
                    try:
                        last_local_id = versions[0].revision.result.local_id
                        revision_create(form, result=True, local_id=last_local_id+1)
                    except:
                        revision_create(form, result=True)
                    task = Simulation.delay(network_id=network_id)
                    
                else:
                    version_obj = Version.objects.get(pk=version_id)
                    
                    # check if it is already simulated, it prevents from simulating.
                    if version_obj.revision.result.is_recorded():
                        response = {'recorded':1}
                        return HttpResponse(cjson.encode(response), mimetype='application/json')
                    else:
                        task = Simulation.delay(network_id=network_id, version_id=version_id)
                    
                response = {'task_id':task.task_id}
                return HttpResponse(cjson.encode(response), mimetype='application/json')
                    
            else:
                responseHTML = render_to_string('network_form.html', {'form': form})
                response = {'responseHTML':responseHTML, 'valid': -1}
                return HttpResponse(cjson.encode(response), mimetype='application/json')
            
        else:
            # check if task_id exists, then a simulation will be aborted.
            if 'task_id' in request.GET:            
                task_id = request.GET.get('task_id')
                abortable_async_result = AbortableAsyncResult(task_id)
                abortable_async_result.abort()
                                
                response = {'aborted':1}
                return HttpResponse(cjson.encode(response), mimetype='application/json')
                
    return HttpResponse()

def default_layout(request, network_id):
    network_obj = get_object_or_404(Network, pk=network_id)
    if request.is_ajax():
        device_list = network_obj.device_list()
        edgelist = network_obj.connections(modeltype='neuron')
        pos = networkx(edgelist, layout='circo')

        for gid,value in pos.items():
            if int(device_list[gid-1][0]['id']) == gid:
                device_list[gid-1][0]['position'] = list(value)
        
        devices_json = cjson.encode(device_list)
        network_obj.devices_json = devices_json
        network_obj.save()
        
        return HttpResponse(devices_json, mimetype='application/json')

    return HttpResponse()