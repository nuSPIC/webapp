from network.models import Network

def check_json_loads():
    network_list = Network.objects.all().order_by('id')
    error_list = []
    for network_obj in network_list:
        try:
            network_obj.nodes()
            network_obj.links()
            network_obj.spike_detector_data()
            network_obj.voltmeter_data()
        except:
            error_list.append(network_obj.id)
    print 'List of networks with broken json loads:', error_list
    return error_list

if __name__ == '__main__':
    check_json_loads()
