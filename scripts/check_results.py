from network.models import Network
import numpy as np

def check_default_json(network_obj):
    return len(network_obj.voltmeter_json) == 0, len(network_obj.spike_detector_json) == 0

def check_empty_data(network_obj):
    errorlist = [False, False]
    voltmeter_data = network_obj.voltmeter_data()
    if len(voltmeter_data['meta']['neurons']) == 0:
        if 'V_m' in voltmeter_data:
            errorlist[0] = True

    spike_detector_data = network_obj.spike_detector_data()
    if len(spike_detector_data['meta']['connect_to']) == 0:
        if 'senders' in spike_detector_data:
            errorlist[1] = True
    else:
        if not 'senders' in spike_detector_data:
            errorlist[1] = True
    return errorlist

def check_has_data(network_obj):
    errorlist = [False, False]
    voltmeter_data = network_obj.voltmeter_data()
    if len(voltmeter_data['meta']['connect_to']) > 0:
        if len(network_obj.voltmeter_json) > 100.:
            if not network_obj.has_voltmeter:
                errorlist[0] = True
    elif network_obj.has_voltmeter:
        errorlist[0] = True

    spike_detector_data = network_obj.spike_detector_data()
    if len(spike_detector_data['meta']['connect_to']) > 0:
        if 'senders' in spike_detector_data:
            if len(spike_detector_data['senders']) > 0:
                if not network_obj.has_spike_detector:
                    errorlist[1] = True
    elif network_obj.has_spike_detector:
        errorlist[1] = True
    return errorlist

def check_meta_neurons(network_obj):
    errorlist = [False, False]
    voltmeter_data = network_obj.voltmeter_data()
    if len(voltmeter_data['meta']['neurons']) > 0:
        if len(voltmeter_data['meta']['neurons'][0].keys()) > 2:
            errorlist[0] = True

    spike_detector_data = network_obj.spike_detector_data()
    if len(spike_detector_data['meta']['neurons']) > 0:
        if len(spike_detector_data['meta']['neurons'][0].keys()) > 2:
            errorlist[1] = True
    return errorlist

def check_date_simulated(network_obj):
    voltmeter_data = network_obj.voltmeter_data()
    spike_detector_data = network_obj.spike_detector_data()
    if network_obj.has_spike_detector or network_obj.has_voltmeter:
        if network_obj.date_simulated is None:
            return True
    else:
        if network_obj.date_simulated is not None:
            return True
    return False

def run(detailed=True):
    print 'Check errors of json-based results'
    color = ['\033[1;31m%s\033[00m', '\033[01;32m%s\033[00m']
    network_list = Network.objects.all().order_by('id')
    error_list = []
    if detailed:
        print 'ID\tdefault json\tempty data\tmeta neurons\thas data\tdate simulated\tany error'
    for network_obj in network_list:
        default_json = check_default_json(network_obj)
        empty_data = check_empty_data(network_obj)
        meta_neurons = check_meta_neurons(network_obj)
        has_data = check_has_data(network_obj)
        date_simulated = check_date_simulated(network_obj)
        error_all = np.array([np.array(default_json).any(), np.array(empty_data).any(), np.array(has_data).any(), np.array(meta_neurons).any(), date_simulated]).any()

        if error_all:
            error_list.append(network_obj)

        if detailed:
            print network_obj.id,'\t',
            print color[default_json[0]]%default_json[0],color[default_json[1]]%default_json[1],'\t',
            print color[empty_data[0]]%empty_data[0],color[empty_data[1]]%empty_data[1],'\t',
            print color[meta_neurons[0]]%meta_neurons[0],color[meta_neurons[1]]%meta_neurons[1],'\t',
            print color[has_data[0]]%has_data[0],color[has_data[1]]%has_data[1],'\t',
            print color[date_simulated]%date_simulated, '\t\t',
            print "|", color[error_all]%error_all

    print 'Network ids with errors: ', [error_network.id for error_network in error_list]
    return error_list

if __name__ == '__main__':
    run(False)
