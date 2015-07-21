import networkx as nx

STATUS_FIELDS = {
    'hh_psc_alpha': ('V_m', 'E_L', 'g_L', 'C_m', 'tau_ex', 'tau_in', 'E_Na', 'g_Na', 'E_K', 'g_K', 'Act_m', 'Act_h', 'Inact_n', 'I_e'),
    'iaf_cond_alpha': ('V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e'),
    'iaf_neuron': ('V_m', 'E_L', 'C_m', 'tau_m', 't_ref', 'V_th', 'V_reset', 'tau_syn', 'I_e'),
    'iaf_psc_alpha': ('V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'tau_syn_ex', 'tau_syn_in', 'I_e'),
    'ac_generator': ('amplitude', 'offset', 'phase', 'frequency'),
    'dc_generator': ('amplitude',),
    'noise_generator': ('mean', 'std', 'dt', 'start', 'stop'),
    'poisson_generator': ('origin', 'rate', 'start', 'stop'),
    'smp_generator': ('dc', 'ac', 'freq', 'phi'),
    'spike_generator': ('start', 'stop', 'spike_times', 'spike_weights'),
}

def networkx(edgelist, layout='neato'):
    ''' Return position of neurons in network. '''
    G = nx.DiGraph()
    G.add_edges_from(edgelist)
    return nx.graphviz_layout(G, layout)

