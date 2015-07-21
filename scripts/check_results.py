def default_json(network_obj):
    return len(network_obj.voltmeter_json) != 0, len(network_obj.spike_detector_json) != 0

def empty_data(network_obj):
    clean = [True, True]
    voltmeter_data = network_obj.voltmeter_data()
    if len(voltmeter_data['meta']['neurons']) == 0:
        if 'V_m' in voltmeter_data:
            clean[0] = False

    spike_detector_data = network_obj.spike_detector_data()
    if len(spike_detector_data['meta']['connect_to']) == 0:
        if 'senders' in spike_detector_data:
            clean[1] = False
    else:
        if not 'senders' in spike_detector_data:
            clean[1] = False
    return clean

def has_data(network_obj):
    clean = [True, True]
    voltmeter_data = network_obj.voltmeter_data()
    if len(voltmeter_data['meta']['connect_to']) > 0:
        if len(network_obj.voltmeter_json) > 100.:
            if not network_obj.has_voltmeter:
                clean[0] = False
    elif network_obj.has_voltmeter:
        clean[0] = False

    spike_detector_data = network_obj.spike_detector_data()
    if len(spike_detector_data['meta']['connect_to']) > 0:
        if 'senders' in spike_detector_data:
            if len(spike_detector_data['senders']) > 0:
                if not network_obj.has_spike_detector:
                    clean[1] = False
    elif network_obj.has_spike_detector:
        clean[1] = False
    return clean

def meta_neurons(network_obj):
    clean = [True, True]
    voltmeter_data = network_obj.voltmeter_data()
    if len(voltmeter_data['meta']['neurons']) > 0:
        if len(voltmeter_data['meta']['neurons'][0].keys()) > 2:
            clean[0] = False

    spike_detector_data = network_obj.spike_detector_data()
    if len(spike_detector_data['meta']['neurons']) > 0:
        if len(spike_detector_data['meta']['neurons'][0].keys()) > 2:
            clean[1] = False
    return clean

def date_simulated(network_obj):
    voltmeter_data = network_obj.voltmeter_data()
    spike_detector_data = network_obj.spike_detector_data()
    if network_obj.has_spike_detector or network_obj.has_voltmeter:
        return network_obj.date_simulated is not None
    else:
        return network_obj.date_simulated is None
