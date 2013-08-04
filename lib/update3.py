

from network.models import Network

network_list = Network.objects.all()

for network_obj in network_list:

    sd_data = network_obj.spike_detector_data()
    if len(sd_data['meta']['neurons']) > 0:
        network_obj.has_spike_detector = True
    else:
        network_obj.has_spike_detector = False

    vm_data = network_obj.voltmeter_data()
    if len(sd_data['meta']['neurons']) > 0:
        network_obj.has_voltmeter = True
    else:
        network_obj.has_voltmeter = False

    network_obj.save()


