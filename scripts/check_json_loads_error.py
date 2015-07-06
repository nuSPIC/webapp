from network.models import Network

def run():
    network_list = Network.objects.all().order_by('id')
    for network_obj in network_list:
        try:
            network_obj.spike_detector_data()
            network_obj.voltmeter_data()
        except:
            print network_obj.id

