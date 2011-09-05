from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import simplejson

from lib.decorators import render_to
from network.templatetags.network_filters import readable

from models import Result
from forms import CommentForm

import cjson

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
	
    response = HttpResponse(cjson.encode(response), mimetype='application/force-download')
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
    status = V_m['status']
    assert (len(voltmeter['times']) == len(V_m['values']))
    response = {
	'values': V_m['values'],
	'times': voltmeter['times'],
	'name': '%s [%s]' %(readable(status[0]['label']), status[0]['id']),
	}
    return {'voltmeter': cjson.encode(response)}
    
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
    Large View of Spike Detector data (its the same like small view of itself)
    """
    
    result_obj = get_object_or_404(Result, pk=result_id)
    spike_detector = result_obj.spike_detector_data()
    assert len(spike_detector['senders']) == len(spike_detector['times'])
    spike_detector['neurons'] = [nn[0]['id'] for nn in result_obj.network.device_list(modeltype='neuron')]
    spike_detector['simTime'] = result_obj.revision.version_set.all()[0].object_version.object.duration
    return spike_detector  
    
@render_to('spike_detector_thumbnail.html')
def spike_detector_thumbnail(request, result_id):
    """
    Small View of Spike Detector data
    """
    
    result_obj = get_object_or_404(Result, pk=result_id)
    spike_detector = result_obj.spike_detector_data()
    assert len(spike_detector['senders']) == len(spike_detector['times'])
    spike_detector['neurons'] = [nn[0]['id'] for nn in result_obj.network.device_list(modeltype='neuron')]
    spike_detector['simTime'] = result_obj.revision.version_set.all()[0].object_version.object.duration
    return spike_detector