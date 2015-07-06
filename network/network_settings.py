
PARAMS_ORDER = {
    "hh_psc_alpha": (
        ['id', 'model'],
        ['targets', 'weight', 'delay', 'V_m', 'E_L', 'g_L', 'C_m', 'tau_ex', 'tau_in', 'E_Na', 'g_Na', 'E_K', 'g_K', 'Act_m', 'Act_h', 'Inact_n', 'I_e']),
    "iaf_cond_alpha": (
        ['id', 'model'],
        ['targets', 'weight', 'delay', 'V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e']),
    "iaf_neuron": (
        ['id', 'model'],
        ['targets', 'weight', 'delay', 'V_m', 'E_L', 'C_m', 'tau_m', 't_ref', 'V_th', 'V_reset', 'tau_syn', 'I_e']),
    "iaf_psc_alpha": (
        ['id', 'model'],
        ['targets', 'weight', 'delay', 'V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e']),
    "parrot": (
        ['id', 'model',],
        []),
    "ac_generator": (
        ['id', 'model',],
        ['amplitude', 'frequency', 'offset', 'phase']),
    "dc_generator": (
        ['id', 'model', 'amplitude'],
        []),
    "noise_generator": (
        ['id', 'model', 'mean'], 
        ['std', 'dt', 'start', 'stop']),
    "poisson_generator": (
        ['id', 'model', 'rate'],
        ['start', 'stop']),
    "smp_generator": (
        ['id', 'model'],
        ['dc', 'ac', 'freq', 'phi']),
    "spike_generator": (
        ['id', 'model', 'spike_times'],
        ['start', 'stop', 'step']),
    "spike_detector": (
        ['id', 'model'],
        []),
    "voltmeter": (
        ['id', 'model'],
        []),
    }

ALL_PARAMS_ORDER = {}
for key, val in PARAMS_ORDER.items():
    ALL_PARAMS_ORDER[key] = val[0] + val[1]
