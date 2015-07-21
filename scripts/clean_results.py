import anyjson as json
import datetime

def default_json(network_obj):
    if len(network_obj.voltmeter_json) == 0:
        network_obj.voltmeter_json = '{"meta":{"neurons":[]}}'
        network_obj.save()
    if len(network_obj.spike_detector_json) == 0:
        network_obj.spike_detector_json = '{"meta":{"neurons":[]}}'
        network_obj.save()

def empty_data(network_obj):
    spike_detector_data = network_obj.spike_detector_data()
    if len(spike_detector_data['meta']['connect_to']) == 0:
        if 'senders' in spike_detector_data:
            network_obj.spike_detector_json = '{"meta":{"neurons":[]}}'
            network_obj.save()
    else:
        if not 'senders' in spike_detector_data:
            network_obj.spike_detector_json = '{"meta":{"neurons":[]}, "senders":[], "times":[]}'
            network_obj.save()

def meta_neurons(network_obj):
    spike_detector_data = network_obj.spike_detector_data()
    if len(spike_detector_data['meta']['neurons']) > 0:
        if len(spike_detector_data['meta']['neurons'][0].keys()) > 2:
            new_neurons = []
            for n in spike_detector_data['meta']['neurons']:
                new_neurons.append({'id': n['id'], 'uid': n['uid']})
            sd_E = json.loads(network_obj.spike_detector_json)
            sd_E['meta']['neurons'] = new_neurons
            network_obj.spike_detector_json = json.dumps(sd_E)
            network_obj.save()

def has_data(network_obj):
    voltmeter_data = network_obj.voltmeter_data()
    if len(voltmeter_data['meta']['connect_to']) > 0:
        if len(network_obj.voltmeter_json) > 100.:
            network_obj.has_voltmeter = True
            network_obj.save()
    else:
        network_obj.has_voltmeter = False
        network_obj.save()

    spike_detector_data = network_obj.spike_detector_data()
    if len(spike_detector_data['meta']['connect_to']) > 0:
        if 'senders' in spike_detector_data:
            if len(spike_detector_data['senders']) > 0:
                network_obj.has_spike_detector = True
                network_obj.save()
    else:
        network_obj.has_spike_detector = False
        network_obj.save()

def date_simulated(network_obj):
    voltmeter_data = network_obj.voltmeter_data()
    spike_detector_data = network_obj.spike_detector_data()
    if network_obj.has_spike_detector or network_obj.has_voltmeter:
        if network_obj.date_simulated is None:
            network_obj.date_simulated = datetime.datetime.now()
            network_obj.save()
    else:
        if network_obj.date_simulated is not None:
            network_obj.date_simulated = None
