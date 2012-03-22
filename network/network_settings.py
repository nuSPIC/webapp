# -*- coding: utf-8 -*-

SPIC_CHOICES = (('0','Sandbox'),
                ('1','SPIC1'),
                ('2','SPIC2'),
                ('3','SPIC3'),
                ('4','SPIC4'))

PARAMS_ORDER = {
    "hh_psc_alpha": (
        ['id', 'type', 'model', 'label'],
        ['targets', 'weight', 'delay', 'V_m', 'E_L', 'g_L', 'C_m', 'tau_ex', 'tau_in', 'E_Na', 'g_Na', 'E_K', 'g_K', 'Act_m', 'Act_h', 'Inact_n', 'I_e']),
    "iaf_cond_alpha": (
        ['id', 'type', 'model', 'label'],
        ['targets', 'weight', 'delay', 'V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e']),
    "iaf_neuron": (
        ['id', 'type', 'model', 'label'],
        ['targets', 'weight', 'delay', 'V_m', 'E_L', 'C_m', 'tau_m', 't_ref', 'V_th', 'V_reset', 'tau_syn', 'I_e']),
    "iaf_psc_alpha": (
        ['id', 'type', 'model', 'label'],
        ['targets', 'weight', 'delay', 'V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e']),
    "parrot": (
        ['id', 'type', 'model', 'label', 'targets', 'weight', 'delay'],
        []),
    "ac_generator": (
        ['id', 'type', 'model', 'label', 'targets', 'weight', 'delay'],
        ['amplitude', 'frequency', 'offset', 'phase']),
    "dc_generator": (
        ['id', 'type', 'model', 'label', 'targets', 'weight', 'delay', 'amplitude'],
        []),
    "noise_generator": (
        ['id', 'type', 'model', 'label', 'targets', 'weight', 'delay', 'mean'], 
        ['std', 'dt', 'start', 'stop']),
    "poisson_generator": (
        ['id', 'type', 'model', 'label', 'targets', 'weight', 'delay', 'rate'],
        ['start', 'stop']),
    "smp_generator": (
        ['id', 'type', 'model', 'label', 'targets', 'weight', 'delay'],
        ['dc', 'ac', 'freq', 'phi']),
    "spike_generator": (
        ['id', 'type', 'model', 'label', 'targets', 'weight', 'delay', 'spike_times'],
        ['start', 'stop', 'step']),
    "spike_detector": (
        ['id', 'type', 'model', 'label', 'sources'],
        []),
    "voltmeter": (
        ['id', 'type', 'model', 'label', 'targets'],
        []),
    }

ALL_PARAMS_ORDER = {}
for key, val in PARAMS_ORDER.items():
    ALL_PARAMS_ORDER[key] = val[0] + val[1]