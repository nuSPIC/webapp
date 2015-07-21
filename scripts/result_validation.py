from network.models import Network
import numpy as np

import check_results as check
import clean_results as clean

def check_result_validation(detailed=True):
    print 'Check errors of json-based results'
    color = ['\033[1;31m%s\033[00m', '\033[01;32m%s\033[00m']
    network_list = Network.objects.all().order_by('id')
    error_list = []
    for network_obj in network_list:
        default_json = check.default_json(network_obj)
        empty_data = check.empty_data(network_obj)
        meta_neurons = check.meta_neurons(network_obj)
        has_data = check.has_data(network_obj)
        date_simulated = check.date_simulated(network_obj)
        clean_all = np.array([np.array(default_json).all(), np.array(empty_data).all(), np.array(has_data).all(), np.array(meta_neurons).all(), date_simulated]).all()

        if not clean_all:
            error_list.append(network_obj)

        if detailed:
            if network_obj.id % 20 == 0:
                print 'ID\tdefault json\tempty data\tmeta neurons\thas data\tdate simulated\tall clean'
            print network_obj.id,'\t',
            print color[default_json[0]]%default_json[0],color[default_json[1]]%default_json[1],'\t',
            print color[empty_data[0]]%empty_data[0],color[empty_data[1]]%empty_data[1],'\t',
            print color[meta_neurons[0]]%meta_neurons[0],color[meta_neurons[1]]%meta_neurons[1],'\t',
            print color[has_data[0]]%has_data[0],color[has_data[1]]%has_data[1],'\t',
            print color[date_simulated]%date_simulated, '\t\t',
            print "|", color[clean_all]%clean_all

    print 'Network ids with errors:', [error_network.id for error_network in error_list]
    return error_list

def clean_results(network_list=None):
    if network_list is None:
        network_list = Network.objects.all().order_by('id')
    count = len(network_list)
    for idx, network_obj in enumerate(network_list):
        print network_obj.id,
        clean.default_json(network_obj); print '.',
        clean.empty_data(network_obj); print '.',
        clean.meta_neurons(network_obj); print '.',
        clean.has_data(network_obj); print '.',
        clean.date_simulated(network_obj); print '.',
        print "cleaned \t (%.1f" %((1.0 - float(idx+1)/count)*100.0), "% remain)"

        network_obj.save()

if __name__ == '__main__':
    error_list = check_result_validation(False)
    if error_list:
        clean_results(error_list)
        check_result_validation(False)
