from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import simplejson

from celery.contrib.abortable import AbortableAsyncResult
from reversion.models import Version
from reversion import revision

from lib.decorators import render_to
from lib.drawers import networkx
from lib.tasks import Simulation

from network.models import Network
from network.helpers import values_extend
from network.forms import *

from result.models import Result
from result.forms import CommentForm


# Define models with its label, modeltypes and form
MODELS = [
    {'id_label': 'iaf_neuron', 		'model_type': 'neuron', 'form': DeviceForm,},
    {'id_label': 'iaf_psc_alpha', 	'model_type': 'neuron', 'form': IafPscAlphaForm,},
    {'id_label': 'ac_generator', 	'model_type': 'input', 	'form': ACGeneratorForm,},
    {'id_label': 'dc_generator',	'model_type': 'input', 	'form': DeviceForm,},
    {'id_label': 'poisson_generator',	'model_type': 'input', 	'form': PoissonGeneratorForm,},
    {'id_label': 'noise_generator', 	'model_type': 'input', 	'form': NoiseGeneratorForm,},
    {'id_label': 'spike_detector', 	'model_type': 'output', 'form': SpikeDetectorForm,},
    {'id_label': 'voltmeter', 		'model_type': 'output', 'form': DeviceForm,},
]

@revision.create_on_success
def revision_create(obj, result=False, **kwargs):
    obj.save()
    if result:
	revision.add_meta(Result, **kwargs)


@render_to('network.html')
@login_required
def network(request, SPIC_id, local_network_id):
    """
    Main view for network workplace
    """
    
    # Check if prototype exists
    prototype = get_object_or_404(Network, user_id=0, SPIC_id=SPIC_id, local_network_id=local_network_id)

    # If network is created, then it create a copy from prototype and an initial version of network.
    network_obj, created = Network.objects.get_or_create(user_id=request.user.pk, SPIC_id=SPIC_id, local_network_id=local_network_id)
    if created:
	network_obj.devices_json = prototype.devices_json
	revision_create(network_obj)

    # Get a list of network versions in reverse date is created.
    versions = Version.objects.get_for_object(network_obj).reverse()
    
    # If request is POST, then it executes any deletions
    if request.method == "POST":
	
	# Delete selected devices from database.
	if request.POST.get('version_ids'):
	    version_ids = request.POST.getlist('version_ids')
	    try:
		for version_id in version_ids:
		    del_version = Version.objects.get(id=int(version_id))
		    del_version.delete()
	    except:
		pass
	
	# Delete selected versions of history.
	elif request.POST.get('device_ids'):
	    device_ids = [int(device_id) for device_id in request.POST.getlist('device_ids')]
	    device_list = [dev for dev in network_obj.device_list() if not dev[0] in device_ids]
	    network_obj.devices_json = simplejson.dumps(device_list)
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
	formsHTML = render_to_string('device_form.html', {'id_label':device['id_label'], 'form':device['form'](network_obj=network_obj)})
	device_formsets.append({'id_label':device['id_label'], 'formsHTML':formsHTML})
	
    # If a version is selected , then it reverts selected version, otherwise it sets version id to 0.
    version_id = request.GET.get('version_id')
    if version_id:
	version = Version.objects.get(id=version_id)
	version.revision.revert()
	network_obj = Network.objects.get(user_id=request.user.pk, SPIC_id=SPIC_id, local_network_id=local_network_id)
    else:
	version_id = 0

    # If result exist, then get form for comment.
    try:
	result_obj = version.revision.result
	comment_form = CommentForm(instance=result_obj)
    except:
	result_obj = None

    # Create an image of network layout and get its url.
    try:
	networkx_url = networkx(network_obj.pk)
    except:
	networkx_url = None
    
    response = {
	'network_obj': network_obj,
	'network_form': NetworkForm(instance=network_obj),
	'device_choices': device_choices,
	'device_formsets': device_formsets,
	'versions': versions,
	'version_id': version_id,
	'networkx_url': networkx_url
    }
	
    if result_obj:
	response['result_obj'] = result_obj
	response['comment_form'] = comment_form
	
    return response


def device_preview(request, network_id):
    """
    Check POST request for validation without saving it in database.
    """
    
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
		model = {'label':label, 'type':modeltype}
		
		# in case sources is found, it doesn't save weight and delay.
		if 'targets' in data:
		    params = {'targets': data.pop('targets')[0], 'weight': data.pop('weight')[0], 'delay': data.pop('delay')[0]}
		elif 'sources' in data:
		    params = {'sources': data.pop('sources')[0]}
		status = {}
		
		# save status of each divices.
		for key, value in data.items():
		    status[key] = value
		    
		response = {'valid': 1, 'device':[None, model, status, params]}
		
	    else:
		response = {'valid': -1, 'id_label':id_label}
	
	    responseHTML = render_to_string('device_form.html', {'id_label':device['id_label'], 'form':form})
	    response['responseHTML'] = responseHTML
	    return HttpResponse(simplejson.dumps(response), mimetype='application/json')
		    
    return HttpResponse()

def device_commit(request, network_id):
    """
    Extend targets/sources and write devices in database.
    """
    
    network_obj = get_object_or_404(Network, pk=network_id)
    
    if request.method == 'POST':
	post = request.POST
	devices = {}
	for k in post.keys():
	    
	    # execute only if the key starts with device_list.
	    if k.startswith('device_list'):
		rest = k[len('device_list'):]
		
		# split the string into different components.
		parts = [p[:-1] for p in rest.split('[')][1:]

		# add a new device in dictionary if it still doesn't exist.
		device_id = int(parts[0])+1
		if device_id not in devices:
		    devices[device_id] = device_id, {}, {}, {}
		    
		# prevent from adding device_id.
		if len(parts) > 2:
		    values = post.get(k)
		    
		    # extend targets or sources and add its values .
		    if 'targets' in parts[2] or 'sources' in parts[2]:
			try:
			    extended_list = values_extend(values, unique=True, toString=True)
			except:
			    extended_list = []

			devices[device_id][int(parts[1])][parts[2]] = ','.join(extended_list)
		
		    # execute only if status value or model label exists.		    
		    elif values:
			    devices[device_id][int(parts[1])][parts[2]] = values
		    

	device_list = devices.values()
	device_list.sort()
	
	network_obj.devices_json = simplejson.dumps(device_list)
	network_obj.save()
	return HttpResponse(simplejson.dumps({'saved':1}), mimetype='application/json')
	    
    return HttpResponse()


def simulate(request, network_id, version_id):
    """
    If version_id is 0, it creates a new version of network and then simulates.
    If already simulated, it won't resimulate.
    If task_id is in request.GET, then it aborts the simulation task.
    """    
    network_obj = get_object_or_404(Network, pk=network_id)
    
    if request.is_ajax():
	if request.method == 'POST':
	    versions = Version.objects.get_for_object(network_obj).reverse()
	    form = NetworkForm(request.POST, instance=network_obj)
	    
	    # check if network form is valid.
	    if form.is_valid():
		
		# if network form is changed or version_id is 0, a new version will be created. 
		# Otherwise it simulates without creating new version.
		if form.has_changed() or int(version_id) == 0:
		    try:
			last_local_result_id = versions[0].revision.result.local_result_id
			revision_create(form, result=True, local_result_id = last_local_result_id+1, user_id = request.user.pk)
		    except:
			revision_create(form, result=True)
		    task = Simulation.delay(network_id=network_id)
		    
		else:
		    version_obj = Version.objects.get(pk=version_id)
		    
		    # check if it is already simulated, it prevents from simulating.
		    if version_obj.revision.result.is_recorded():
			response = {'recorded':1}
			return HttpResponse(simplejson.dumps(response), mimetype='application/json')
		    else:
			task = Simulation.delay(network_id=network_id, version_id=version_id)
		    
		response = {'task_id':task.task_id}
		return HttpResponse(simplejson.dumps(response), mimetype='application/json')
		    
	    else:
		responseHTML = render_to_string('network_form.html', {'form': form})
		response = {'responseHTML':responseHTML, 'valid': -1}
		return HttpResponse(simplejson.dumps(response), mimetype='application/json')
	    
	else:
	    # check if task_id exists, then a simulation will be aborted.
	    if 'task_id' in request.GET:	    
		task_id = request.GET.get('task_id')
		abortable_async_result = AbortableAsyncResult(task_id)
		abortable_async_result.abort()
				
		response = {'aborted':1}
		return HttpResponse(simplejson.dumps(response), mimetype='application/json')
		
    return HttpResponse()
