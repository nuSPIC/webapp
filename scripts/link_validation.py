from network.models import Network

errors = {  'source': {'status': {'model': 'spike_detector'}},
            'target': {'type': 'input', 'status': {'model': 'voltmeter'}}}

def link_validation(link, nodes, nodes_uid):
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

def check_link_validation():
    network_list = Network.objects.all().order_by('id')
    error_list = []
    for network_obj in network_list:
        nodes = network_obj.nodes()
        nodes_uid = [node['uid'] for node in nodes]
        links = network_obj.links()

        for link in links:
            if link_validation(link, nodes, nodes_uid):
                error_list.append(network_obj.id)
    print 'List of networks contain invalid links:', error_list
    return error_list

def clean_link_validation():
    network_list = Network.objects.all().order_by('id')
    error = []
    count = len(network_list)
    for idx, network_obj in enumerate(network_list):
        print network_obj.id,
        nodes = network_obj.nodes()
        nodes_uid = [node['uid'] for node in nodes]
        links = network_obj.links()

        error = False
        links_cleaned = []
        for link in links:
            if not link_validation(link, nodes, nodes_uid):
                links_cleaned.append(link)
            else:
                error = True

        if error:
            network_obj.update(nodes, links_cleaned)
            network_obj.save()
        print "cleaned \t (%.1f" %((1.0 - float(idx+1)/count)*100.0), "% remain)"

if __name__ == '__main__':
    error_list = check_link_validation()
    if error_list:
        clean_link_validation(error_list)
        check_link_validation()
