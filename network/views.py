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

from network.helpers import revision_create, values_extend, id_escape, id_identify
from network.forms import *
from network.models import Network

from result.forms import CommentForm
from result.models import Result

import numpy as np
import os

# Define models with its modeltype, label and form.
MODELS = [
    #{'model_type': 'neuron',  'id_label': 'hh_psc_alpha',         'form': HhPscAlphaForm,},
    {'model_type': 'neuron',  'id_label': 'iaf_cond_alpha',       'form': IafCondAlphaForm,},
    {'model_type': 'neuron',  'id_label': 'iaf_neuron',           'form': IafNeuronForm,},
    {'model_type': 'neuron',  'id_label': 'iaf_psc_alpha',        'form': IafPscAlphaForm,},
    #{'model_type': 'input',   'id_label': 'parrot_neuron',        'form': ParrotForm,},
    
    {'model_type': 'input',   'id_label': 'ac_generator',         'form': ACGeneratorForm,},
    {'model_type': 'input',   'id_label': 'dc_generator',         'form': DCGeneratorForm,},
    {'model_type': 'input',   'id_label': 'poisson_generator',    'form': PoissonGeneratorForm,},
    {'model_type': 'input',   'id_label': 'noise_generator',      'form': NoiseGeneratorForm,},
    #{'model_type': 'input',   'id_label': 'smp_generator',       'form': SmpGeneratorForm,},
    {'model_type': 'input',     'id_label': 'spike_generator',    'form': SpikeGeneratorForm,},   
    
    {'model_type': 'output',  'id_label': 'spike_detector',       'form': TargetForm,},
    {'model_type': 'output',  'id_label': 'voltmeter',            'form': SourceForm,},
]

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
    
@render_to('network_layout.html')
@login_required
def network_layout(request, SPIC_id, local_id):
    network_obj = get_object_or_404(Network, user_id=request.user.pk, SPIC_id=SPIC_id, local_id=local_id)
    
    response = {
        'network_obj': network_obj,
    }
    
    return response
    
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

    version_obj = None
    result_obj = None
    version_id = -1
    
    # Get a list of network versions in reverse date is created.
    versions = Version.objects.get_for_object(network_obj)

    version_term = request.GET.get('version')
    if version_term == 'first' or int(result_id) == 0:
        version_obj = versions[0].revision.revert()
        network_obj = Network.objects.get(user_id=request.user.pk, SPIC_id=SPIC_id, local_id=local_id)
        version_id = 0
        
    else:
        results = [version.revision.result for version in versions[1:]]
        result_ids = [result.local_id for result in results]

        if version_term == 'last':
            result_id = result_ids[-1]

        if int(result_id) in result_ids:
            result_id = result_ids.index(int(result_id))

            version_obj = versions[result_id +1].revision.revert()
            result_obj = results[result_id]
            version_id = versions[result_id +1].revision.result.local_id
            network_obj = Network.objects.get(user_id=request.user.pk, SPIC_id=SPIC_id, local_id=local_id)

    
    # If request is POST, then it executes any deletions
    if request.method == "POST":
        
        # Delete selected devices from database.
        if request.POST.get('version_ids'):
            version_ids = request.POST.getlist('version_ids')
            action = request.POST.get('action')
            for vid in version_ids:
                version_edit = Version.objects.get(pk=int(vid))
                try:
                    result = version_edit.revision.result
                except:
                    result = None
                    
                if action == 'delete':
                    version_edit.delete()
                    if result:
                        result.delete()
                        result_obj = None
                elif action == 'favorite' and result:
                    result.favorite = True
                    result.save()
                elif action == 'unfavorite' and result:
                    result.favorite = False
                    result.save()
        
        # Delete selected device 
        elif request.POST.get('device_ids'):
            
            device_ids = np.array(request.POST.getlist('device_ids'), dtype=int)
            del_vids = device_ids.copy()

            device_dict = network_obj.device_dict()
            id_filterbank = network_obj.id_filterbank()
            device_list = network_obj.device_list()

            for model, status, conns in device_list:
                if model['type'] == 'input' or model['type'] == 'output' and conns != {}:
                    if 'targets' in conns:
                        term = 'targets'
                    elif 'sources' in conns:        
                        term = 'sources'
                        
                    neurons = np.array(conns[term].split(','), dtype=int)
                    del_term = True
                    for neuron in neurons:
                        if not neuron in device_ids:
                            del_term = False
                            
                    if del_term:
                        del_vids = np.append(del_vids, model['id'])

            id_updater = np.zeros(len(device_list))
            id_updater[del_vids-1] = 1
            
            id_updatebank = network_obj.device_list(key='id')
            id_updatebank = np.array([id_updatebank, id_updatebank]).T
            id_updatebank[:,1] -= id_updater.cumsum()

            for model, status, conns in device_list:
               
               
                if not model['id'] in del_vids:
                    # correct device IDs
                    old_id = model['id']
                    tid = id_identify(id_filterbank, old_id)                
                    model['id'] = int(id_escape(id_updatebank, old_id))

                    # delete target/source
                    new_conns = {}
                    if conns != {}:
                        if 'targets' in conns:
                            term = 'targets'
                        elif 'sources' in conns:        
                            term = 'sources'
                            
                        value_list = conns[term].split(',')
                        value_array = np.array([item for item in enumerate(value_list) if int(item[1]) not in del_vids], dtype=int)
                        
                        if value_array.any():
                            value_list = [str(id_escape(id_updatebank, val)) for val in value_array[:,1]]
                                
                            new_conns[term] = ','.join(value_list)
                        
                            # delete weight and delay
                            if 'weight' in conns:
                                weight_list = conns['weight'].split(',')
                                weight_list = [str(item[1]) for item in enumerate(weight_list) if item[0] in value_array[:,0]]
                                if not weight_list == ['']:
                                    new_conns['weight'] = ','.join(weight_list)
                                
                            if 'delay' in conns:
                                delay_list = conns['delay'].split(',')
                                delay_list = [str(item[1]) for item in enumerate(delay_list) if item[0] in value_array[:,0]]
                                if not delay_list == ['']:
                                    new_conns['delay'] = ','.join(delay_list)
                            
                    # merge all status
                    device_dict[('%4d' %tid).replace(' ','0')] = [model, status, new_conns]
                    
            # remove selected device from dict
            new_device_dict = {}
            for old_vid, new_vid in id_updatebank:
                if new_vid > 0 and old_vid not in del_vids:
                    new_device_dict[('%4d' %id_identify(id_filterbank, new_vid)).replace(' ','0')] = device_dict[('%4d' %id_identify(id_filterbank, old_vid)).replace(' ','0')]
                    
            hidden_device_tids = id_identify(id_filterbank, -1)
            for hidden_device_tid in hidden_device_tids:
                new_device_dict[('%4d' %hidden_device_tid).replace(' ','0')] = device_dict[('%4d' %hidden_device_tid).replace(' ','0')]
                
            network_obj.devices_json = json.encode(new_device_dict)
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
        
    root_status = network_obj.root_status()
    if 'rng_seeds' in root_status or 'grng_seed' in root_status:
        if root_status['rng_seeds'] == [1] or root_status['grng_seed'] == 1:
            network_form = NetworkForm(instance=network_obj, initial={'same_seed': True})
        else:
            network_form = NetworkForm(instance=network_obj, initial={'same_seed': False})
    else:
        network_form = NetworkForm(instance=network_obj, initial={'same_seed': True})
        
    response = {
        'network_obj': network_obj,
        'network_form': network_form,
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
          
            post = request.POST
            id_label = post.get('model')
            id_labels = [device['id_label'] for device in MODELS]
            device = MODELS[id_labels.index(id_label)]
            form = device['form'](network_obj, post)

            # check if form is valid.
            if form.is_valid():
                data = form.data.copy()
                data.pop('csrfmiddlewaretoken')
                data.pop('neuron_ids')
                label = data.pop('model')[0]
                
                # get modeltype of device.
                model = {'id': None, 'label':label}
                if 'generator' in label:
                    model['type'] = 'input'
                elif 'meter' in label or 'detector' in label:
                    model['type'] = 'output'
                else:
                    model['type'] = 'neuron'
                
                # get sources or targets.
                if 'targets' in data:
                    term = 'targets'
                elif 'sources' in data:
                    term = 'sources'
                    
                # it doesn't save weight, delay and synapse_type, if they don't exist.
                conns = {term: data.pop(term)[0]}
                if 'weight' in data:
                    conns['weight'] = data.pop('weight')[0]
                if 'delay' in data:
                    conns['delay'] = data.pop('delay')[0]
                    
                if 'synapse_type' in data:
                    synapse_type = data.pop('synapse_type')[0]
                    if synapse_type != 'static_synapse':
                        conns['synapse_type'] = synapse_type
                            
                if not conns[term]:
                    conns = {}
                    
                # after poping connection information save status of divices.
                status = {}
                for key, value in data.iteritems():
                    if form.fields[key].initial:
                        if value and float(value) != float(form.fields[key].initial):
                            status[key] = value
                    else:
                        status[key] = value
                        
                if id_label == 'spike_generator' and 'step' in status:
                    if status['step']:
                        status.pop('step')
                    
                response = {'valid': 1, 'device':[model, status, conns]}
                
            else:
                response = {'valid': -1, 'id_label':id_label}
        
            responseHTML = render_to_string('device_form.html', {'id_label':device['id_label'], 'form':form})
            response['responseHTML'] = responseHTML
            return HttpResponse(json.encode(response), mimetype='application/json')
                    
    return HttpResponse()

def device_commit(request, network_id):
    """ AJAX: Extend targets/sources and write devices in database. """
    
    network_obj = get_object_or_404(Network, pk=network_id)

    if request.is_ajax():
        if request.method == 'POST':

            post = request.POST
            device_list = json.decode(str(post['devices_json']))
            
            device_dict = network_obj.device_dict()
            edgelist = network_obj.connections(modeltype='neuron')
            id_filterbank = network_obj.id_filterbank()
            layoutSize = network_obj.layout_size()
            
            for gid, device in enumerate(device_list):
                model, status, conns = device

                if model['type'] == 'neuron':
                    if 'targets' in conns:
                        extended_list = values_extend(conns['targets'], unique=True)
                        extended_converted_list = [str(id_identify(id_filterbank, vid)) for vid in extended_list if vid in id_filterbank[:,1]]
                        if extended_converted_list:
                            device[2]['targets'] = ','.join(extended_converted_list)

                    if not 'position' in model:
                        device[0]['position'] = [np.random.random_integers(17, layoutSize['x']), np.random.random_integers(14, layoutSize['y']+30)]
                 
                    if id_filterbank.any():
                        tid = id_identify(id_filterbank, device[0]['id'])
                        if not tid:
                            tid = id_filterbank[-1][0]+1
                            id_filterbank = np.append(id_filterbank, np.array([[tid, device[0]['id']]], dtype=int), axis=0)
                    else:
                        tid = 1
                        id_filterbank = np.array([[tid, device[0]['id']]], dtype=int)
                    device_dict[('%4d' %tid).replace(' ', '0')] = device

            for gid, device in enumerate(device_list):
                model, status, conns = device
                
                if model['type'] != 'neuron':
                    if 'targets' in conns or 'sources' in conns:
                        if 'targets' in conns:
                            term = 'targets'
                        else:
                            term = 'sources'

                        extended_list = values_extend(conns[term], unique=True)
                        extended_converted_list = [str(id_identify(id_filterbank, vid)) for vid in extended_list if vid in id_filterbank[:,1]]
                        if extended_converted_list:
                            device[2][term] = ','.join(extended_converted_list)

                    tid = id_identify(id_filterbank, device[0]['id'])
                    if not tid:
                        tid = id_filterbank[-1][0]+1
                        id_filterbank = np.append(id_filterbank, np.array([[tid, device[0]['id']]], dtype=int), axis=0)
                    device_dict[('%4d' %tid).replace(' ', '0')] = device

            network_obj.devices_json = json.encode(device_dict)
            network_obj.save()
            
            if edgelist != network_obj.connections(modeltype='neuron'):
                default_layout(request, network_obj.pk)
            return HttpResponse(json.encode({'saved':1}), mimetype='application/json')
            
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
            device_list = json.decode(str(post['devices_json']))
            
            edgelist = network_obj.connections(modeltype='neuron')
            device_dict = network_obj.device_dict()

            id_filterbank = network_obj.id_filterbank()
            for gid, device in enumerate(device_list):
                model, status, conns = device
                
                cleaned_status = {}
                for status_key, status_value in status.iteritems():
                    if status_value:
                        cleaned_status[status_key] = status_value
                device[1] = cleaned_status
                
                if 'targets' in conns or 'sources' in conns:
                    if 'targets' in conns:
                        term = 'targets'
                    else:
                        term = 'sources'
                        
                    try:
                        extended_list = values_extend(conns[term], unique=True)
                        extended_converted_list = [str(id_identify(id_filterbank, vid)) for vid in extended_list]
                    except:
                        extended_converted_list = []
                        
                    device[2][term] = ','.join(extended_converted_list)

                if id_filterbank.any():
                    tid = id_identify(id_filterbank, device[0]['id'])
                    if not tid:
                        tid = id_filterbank[-1][0]+1
                        id_filterbank = np.append(id_filterbank, np.array([[tid, device[0]['id']]], dtype=int), axis=0)
                else:
                    tid = 1
                    id_filterbank = np.array([[tid, device[0]['id']]], dtype=int)
                device_dict[('%4d' %tid).replace(' ', '0')] = device

                        
            network_obj.devices_json = json.encode(device_dict)
            network_obj.save()
            
            if edgelist != network_obj.connections(modeltype='neuron'):
                default_layout(request, network_obj.pk)
            
            form = NetworkForm(request.POST, instance=network_obj)
            versions = Version.objects.get_for_object(network_obj).reverse()
            
            # check if network form is valid.
            if form.is_valid():

                # if network form is changed or version_id is 0, a new version will be created. 
                # Otherwise it simulates without creating new version.
                if form.has_changed():
                    version_id = 0
                    
                if form.cleaned_data['same_seed']:
                    root_status = {'rng_seeds': [1], 'grng_seed': 1}
                else:
                    rng_seeds, grng_seed = np.random.random_integers(0,1000,2)
                    root_status = {'rng_seeds': [int(rng_seeds)], 'grng_seed': int(grng_seed)}
                    
                network_obj.status_json = json.encode(root_status)
                network_obj.save()        
                        
                if int(version_id) > 0:
                    # check if it is already simulated, it prevents from simulating.
                    version_obj = Version.objects.get(pk=version_id)
                    if version_obj.revision.result.is_recorded():
                        response = {'recorded':1}
                        return HttpResponse(json.encode(response), mimetype='application/json')
                        
                try:
                    last_local_id = versions[0].revision.result.local_id
                    revision_create(form, result=True, local_id=last_local_id+1)
                except:
                    revision_create(form, result=True)

                task = Simulation.delay(network_id=network_id, form=form, version_id=version_id)
                    
                response = {'task_id':task.task_id}
                return HttpResponse(json.encode(response), mimetype='application/json')
                    
            else:
                responseHTML = render_to_string('network_form.html', {'form': form})
                response = {'responseHTML':responseHTML, 'valid': -1}
                return HttpResponse(json.encode(response), mimetype='application/json')
            
        else:
            # check if task_id exists, then a simulation will be aborted.
            if 'task_id' in request.GET:            
                task_id = request.GET.get('task_id')
                abortable_async_result = AbortableAsyncResult(task_id)
                abortable_async_result.abort()
                                
                response = {'aborted':1}
                return HttpResponse(json.encode(response), mimetype='application/json')
                
    return HttpResponse()

def save_layout(request, network_id):
    network_obj = get_object_or_404(Network, pk=network_id)
    
    if request.is_ajax():
        if request.method == 'POST':
        
            post = request.POST
            device_list = json.decode(str(post['devices_json']))
            id_filterbank = network_obj.id_filterbank()
            device_dict = network_obj.device_dict()

            for gid, device in enumerate(device_list):
                model, status, conns = device
                
                if 'position' in model:
                    tid = id_identify(id_filterbank, model['id'])
                    if tid:
                        device_dict[('%4d' %tid).replace(' ', '0')][0]['position'] = model['position']
                
            network_obj.devices_json = json.encode(device_dict)
            network_obj.save()
        
        response = {'layoutSize':network_obj.layout_size()}
        return HttpResponse(json.encode(response), mimetype='application/json')

    return HttpResponse()

def default_layout(request, network_id):
    network_obj = get_object_or_404(Network, pk=network_id)
    
    if request.is_ajax():
        edgelist = network_obj.connections(modeltype='neuron')
        pos = networkx(edgelist, layout='circo')

        device_dict = network_obj.device_dict()
        id_filterbank = network_obj.id_filterbank()
        neuron_id_filterbank = network_obj.neuron_id_filterbank()
        
        for nid, value in pos.iteritems():
            vid = id_identify(neuron_id_filterbank, nid)
            tid = ("%4d" %id_identify(id_filterbank, vid)).replace(" ", "0")
            device_dict[tid][0]['position'] = list(value)
        
        devices_json = json.encode(device_dict)
        network_obj.devices_json = devices_json
        network_obj.save()
        
        response = {'device_list':network_obj.device_list(), 'layoutSize': network_obj.layout_size()}
        return HttpResponse(json.encode(response), mimetype='application/json')

    return HttpResponse()