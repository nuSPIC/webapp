# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import simplejson

from lib.decorators import render_to
import lib.json as json

from network.templatetags.network_filters import readable
from network.helpers import id_escape

from models import Result
from forms import CommentForm


def result_comment(request, result_id):
    """
    Comment forms of result
    """
    
    result_obj = get_object_or_404(Result, pk=result_id)
    
    if request.is_ajax():
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=result_obj)
            result_obj = form.save()
            return HttpResponse(result_obj.comment)
        
    return HttpResponse()

def data(request, result_id):
    result_obj = get_object_or_404(Result, pk=result_id)
    
    voltmeter = result_obj.voltmeter_data()
    spike_detector = result_obj.spike_detector_data()
    
    response = {
        'voltmeter': voltmeter,
        'spike_detector' : spike_detector,
    }
    
    response = HttpResponse(json.encode(response), mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s_%s.txt' %(result_obj.network, result_obj)

    return response


@render_to('voltmeter.html')
def voltmeter(request, result_id):
    """
    Large View of Voltmeter data for selected neuron (sender)
    """
    
    result_obj = get_object_or_404(Result, pk=result_id)
    neuron = int(request.GET.get('neuron'))
    
    voltmeter = result_obj.voltmeter_data(neuron)
    V_m = voltmeter['V_m'][0]
    assert (len(voltmeter['times']) == len(V_m['values']))
    status = V_m['status']

    response = {
        'values': V_m['values'],
        'times': voltmeter['times'],
        'name': '%s [%s]' %(readable(status[0]['label']), status[0]['id']),
    }
    
    return {'voltmeter': json.encode(response)}
    
@render_to('voltmeter_thumbnail.html')
def voltmeter_thumbnail(request, result_id):
    """
    Small View of Voltmeter data
    """
    
    result_obj = get_object_or_404(Result, pk=result_id)
    return {'result_obj': result_obj}

@render_to('spike_detector.html')
def spike_detector(request, result_id):
    """
    View of Spike Detector data
    """
    
    result_obj = get_object_or_404(Result, pk=result_id)
    network_obj = result_obj.network
    output_list = network_obj.device_list(modeltype='output')
    
    spike_detector = result_obj.spike_detector_data()
    assert len(spike_detector['senders']) == len(spike_detector['times'])

    neurons = network_obj.neuron_ids()
    spike_detector['neurons'] = network_obj._connect_to(label='spike_detector')
    spike_detector['neuronScale'] = [ii+1 for ii,v in enumerate(spike_detector['neurons'])]

    id_filterbank = network_obj.id_filterbank()
    neuron_id_filterbank = network_obj.neuron_id_filterbank(label="spike_detector")
    spike_detector['senders'] = [id_escape(id_filterbank, sender) for sender in spike_detector['senders']]
    spike_detector['senders'] = [id_escape(neuron_id_filterbank, sender) for sender in spike_detector['senders']]
    
    spike_detector['simTime'] = result_obj.revision.version_set.all()[0].object_version.object.duration
    
    if request.GET.get('view') == 'small':
        spike_detector['fig'] = {'width':250, 'height':300, 'w':210, 'h2':50, 'yticks':3}
    else:
        spike_detector['fig'] = {'width':750, 'height':500, 'w':700, 'h2':150, 'yticks':6}
    
    return spike_detector