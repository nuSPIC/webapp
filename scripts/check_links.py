from network.models import Network

errors = {  'source': {'status': {'model': 'spike_detector'}}, 
            'target': {'type': 'input', 'status': {'model': 'voltmeter'}}}

def check_link_validation(link, nodes, nodes_uid):
    error = False
    for term, values in errors.iteritems():
        node = nodes[nodes_uid.index(link[term])]
        for key, val in values.iteritems():
            if isinstance(val, dict):
                if node[key]['model'] == val['model']:
                    error = True
            if isinstance(val, str):
                if node[key] == val:
                    error = True
    return error

def run():
    network_list = Network.objects.all().order_by('id')
    error_list = []
    for network_obj in network_list:
        nodes = network_obj.nodes()
        nodes_uid = [node['uid'] for node in nodes]
        links = network_obj.links()

        for link in links:
            if check_link_validation(link, nodes, nodes_uid):
                error_list.append(network_obj.id)
    print error_list

if __name__ == '__main__':
    run()

