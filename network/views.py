import anyjson as json
import numpy as np
import os
import re
import time

from celery.contrib.abortable import AbortableAsyncResult

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from lib.decorators import render_to
from lib.delivery import networkx
from lib.helpers import get_flatpage_or_none
from lib.tasks import Simulation

from network.forms import NetworkForm, NetworkCommentForm, LinkForm, NodesCSVForm, NodeForm
from network.models import SPIC, Network


@render_to('network_list.html')
def network_list(request):
    """ Get a list of unchanged networks from architect."""
    flatpage = get_flatpage_or_none(request)
    network_list = Network.objects.filter(user_id=0)

    return {
        'flatpage': flatpage,
        'network_list': network_list,
    }  


@login_required
def network_initial(request, SPIC_group, SPIC_id):
    """ Get the first network or create a copied network from architect."""
    SPIC_obj = get_object_or_404(SPIC, group=SPIC_group, local_id=SPIC_id)
    network_obj, created = Network.objects.get_or_create(user_id=request.user.pk, SPIC=SPIC_obj, local_id=0, deleted=False)
    
    if created is True:
        # Check if prototype exists
        prototype = get_object_or_404(Network, user_id=0, SPIC=SPIC_obj)
        network_obj.nodes_json = prototype.nodes_json
        network_obj.links_json = prototype.links_json
        network_obj.save()

    return network(request, SPIC_group, SPIC_id, 0)

@login_required
def network_latest(request, SPIC_group, SPIC_id):
    """ Get the latest version of network."""
    SPIC_obj = get_object_or_404(SPIC, group=SPIC_group, local_id=SPIC_id)
    network_list = Network.objects.filter(user_id=request.user.pk, SPIC=SPIC_obj).values('id','local_id','label','comment','date_simulated','deleted','favorite').order_by('-id')

    if len(list(network_list)) > 0:
        return network(request, SPIC_group, SPIC_id, network_list[0]['local_id'])
    else:
        return network_initial(request, SPIC_group, SPIC_id)

@render_to('network_history.html')
@login_required
def network_history(request, SPIC_group, SPIC_id):
    """ Get the latest version of network."""
    SPIC_obj = get_object_or_404(SPIC, group=SPIC_group, local_id=SPIC_id)
    network_list = Network.objects.filter(user_id=request.user.pk, SPIC=SPIC_obj).order_by("-local_id")

    return {'SPIC_obj': SPIC_obj, 'network_list': network_list}


@render_to('network_base.html')
@login_required
def network(request, SPIC_group, SPIC_id, local_id):

    SPIC_obj = SPIC.objects.get(group=SPIC_group, local_id=SPIC_id)
    network_list = Network.objects.filter(user_id=request.user.pk, SPIC=SPIC_obj).values('id','local_id','label','comment','date_simulated','deleted','favorite').order_by('-id')
    network_obj = get_object_or_404(Network, user_id=request.user.pk, SPIC__group=SPIC_group, SPIC__local_id=SPIC_id, local_id=local_id)

    # Get root status
    root_status = network_obj.root_status()
    same_seed = True
    if 'rng_seeds' in root_status or 'grng_seed' in root_status:
        if root_status['rng_seeds'] != [1] and root_status['grng_seed'] != 1:
            same_seed = False

    # Prepare for template
    return {
        'SPIC_obj': SPIC_obj,
        'network_list': network_list,
        'network_obj': network_obj,
        'comment_form': NetworkCommentForm(instance=network_obj),
#        'nodes_csv_form': NodesCSVForm({'csv':network_obj.nodes_csv()}),
        'network_form': NetworkForm(instance=network_obj, initial={'same_seed': same_seed}),
        'node_form': NodeForm(),
        'link_form': LinkForm(),
    }



"""
AJAX request
"""

def network_comment(request, network_id):
    network_obj = get_object_or_404(Network, user_id=request.user.pk, pk=network_id)

    if request.is_ajax():
        if request.method == 'POST':
            form = NetworkCommentForm(request.POST, network_obj)
            if form.is_valid():
                network_obj.label = request.POST['label']
                network_obj.comment = request.POST['comment']
                network_obj.save()
                return HttpResponse(json.dumps(request.POST), mimetype='application/json')

    return HttpResponse()


def network_like(request, network_id):
    network_obj = get_object_or_404(Network, user_id=request.user.pk, pk=network_id)
    if request.is_ajax():
        if network_obj.local_id > 0:
            network_obj.favorite = True
            network_obj.save()

    return HttpResponse()


def network_dislike(request, network_id):
    network_obj = get_object_or_404(Network, user_id=request.user.pk, pk=network_id)

    if request.is_ajax():
        if network_obj.local_id > 0:
            network_obj.favorite = False
            network_obj.save()

    return HttpResponse()

def label_save(request, network_id):
    """ AJAX: Save network layout."""
    network_obj = get_object_or_404(Network, pk=network_id)

    if request.is_ajax():
        if request.method == 'POST':
            network_obj.label = request.POST['label']
            network_obj.save()

            response = {'label':network_obj.label}
            return HttpResponse(json.dumps(response), mimetype='application/json')

    return HttpResponse()


def layout_save(request, network_id):
    """ AJAX: Save network layout."""
    network_obj = get_object_or_404(Network, pk=network_id)

    if request.is_ajax():
        if request.method == 'POST':
            deviceList = json.loads(str(request.POST.get('devices_json')))

#            network_obj = network_obj.update(deviceList, force_self=True)
#            network_obj.save()

        return HttpResponse()

    return HttpResponse()

def layout_default(request, network_id):
    """ AJAX: Set network layout to default."""
    network_obj = get_object_or_404(Network, pk=network_id)

    if request.is_ajax():
        nodes = network_obj.nodes()
        links = network_obj.links(out='object')

        edgelist = [[l['source']['uid'], l['target']['uid']] for l in links if l['source']['type'] == 'neuron' and l['target']['type'] == 'neuron']
        pos = networkx(edgelist, layout='circo')

        window = np.array([800.,600.])
#        window = np.array(pos.values()).max(axis=0) + np.array(pos.values()).min(axis=0)
        size = np.array(pos.values()).max(axis=0) + np.array(pos.values()).min(axis=0)
        shift = (window-size)/2

#        pos_norm = {}
#        for j,i in pos.iteritems():
#            pos_norm[j] = (float(i[0]+shift[0]) / window[0], float(i[1]+shift[1]) / window[1])

        pos_norm2 = [(p[0], ((np.array(p[1])+shift)/window).tolist()) for p in pos.items()]

        return HttpResponse(json.dumps({'pos':pos_norm2}), mimetype='application/json')

    return HttpResponse()

def simulate(request, network_id):
    """
    AJAX: If version_id is 0, it creates a new version of network and then simulates.
    If already simulated, it won't resimulate.
    If task_id is in request.GET, then it aborts the simulation task.
    """
    network_obj = get_object_or_404(Network, pk=network_id)

    if request.is_ajax():

        # If request is POST, then it executes any deletions
        if request.method == "POST":
            form = NetworkForm(request.POST, instance=network_obj)

            # check if network form is valid.
            if form.is_valid():
                if form.cleaned_data['overwrite'] is False or network_obj.local_id == 0:
                    sim_obj = network_obj.create_latest()
                    print sim_obj
                else:
                    sim_obj = network_obj

                nodes = json.loads(str(request.POST.get('nodes')))
                links = json.loads(str(request.POST.get('links')))
                sim_obj.update(nodes, links)

                sim_obj.duration = form.cleaned_data['duration']
                # if not same_seed, generate seeds for root_status
                if form.cleaned_data['same_seed']:
                    root_status = {'rng_seeds': [1], 'grng_seed': 1}
                else:
                    rng_seeds, grng_seed = np.random.random_integers(0,1000,2)
                    root_status = {'rng_seeds': [int(rng_seeds)], 'grng_seed': int(grng_seed)}
                sim_obj.status_json = json.dumps(root_status)
                sim_obj.save()
                time.sleep(1)
                task = Simulation.delay(sim_obj.pk)

                return HttpResponse(task.task_id)

    return HttpResponse()

def abort(request, task_id):

    abortable_async_result = AbortableAsyncResult(task_id)
    abortable_async_result.abort()

    return HttpResponse()

def data(request, network_id):
    network_obj = get_object_or_404(Network, pk=network_id)
    
    response = {
        'nodes': network_obj.nodes(),
        'links': network_obj.links(),
        'result' : {}
    }
    
    if network_obj.has_voltmeter:
        response['result']['voltmeter'] = network_obj.voltmeter_data()
        
    if network_obj.has_spike_detector:
        response['result']['spike_detector'] = network_obj.spike_detector_data()
    
    response = HttpResponse(json.dumps(response), mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s_%s_%s.json' %(network_obj.date_simulated.strftime('%y%m%d'), network_obj.SPIC, network_obj.local_id)

    return response

