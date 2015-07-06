from network.models import Network
import anyjson as json
import datetime

def clean_default_json(network_obj):
    if len(network_obj.voltmeter_json) == 0:
        network_obj.voltmeter_json = '{"meta":{"neurons":[]}}'
        network_obj.save()
    if len(network_obj.spike_detector_json) == 0:
        network_obj.spike_detector_json = '{"meta":{"neurons":[]}}'
        network_obj.save()

def clean_empty_data(network_obj):
    spike_detector_data = network_obj.spike_detector_data()
    if len(spike_detector_data['meta']['connect_to']) == 0:
        if 'senders' in spike_detector_data:
            network_obj.spike_detector_json = '{"meta":{"neurons":[]}}'
            network_obj.save()
    else:
        if not 'senders' in spike_detector_data:
            network_obj.spike_detector_json = '{"meta":{"neurons":[]}, "senders":[], "times":[]}'
            network_obj.save()

def clean_meta_neurons(network_obj):
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

def clean_has_data(network_obj):
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

def clean_date_simulated(network_obj):
    voltmeter_data = network_obj.voltmeter_data()
    spike_detector_data = network_obj.spike_detector_data()
    if network_obj.has_spike_detector or network_obj.has_voltmeter:
        if network_obj.date_simulated is None:
            network_obj.date_simulated = datetime.datetime.now()
            network_obj.save()
    else:
        if network_obj.date_simulated is not None:
            network_obj.date_simulated = None
            network_obj.save()

def run(network_list=None):
    if network_list is None:
        network_list = Network.objects.all().order_by('id')
    count = len(network_list)
    for idx, network_obj in enumerate(network_list):
        print network_obj.id,
        clean_default_json(network_obj); print '.',
        clean_empty_data(network_obj); print '.',
        clean_meta_neurons(network_obj); print '.',
        clean_has_data(network_obj); print '.',
        clean_date_simulated(network_obj); print '.',
        print "cleaned \t (%.1f" %((1.0 - float(idx+1)/count)*100.0), "% remain)"

if __name__ == '__main__':
    import scripts.check_results as check
    error_list = check.run(False)
    if error_list:
        run(error_list)
        check.run(False)
