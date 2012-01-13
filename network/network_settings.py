# -*- coding: utf-8 -*-

SPIC_CHOICES = (('0','Sandbox'),
                ('1','SPIC1'),
                ('2','SPIC2'),
                ('3','SPIC3'),
                ('4','SPIC4'))

PARAMS_ORDER = {
    "hh_psc_alpha": (
        [],
        ['V_m', 'E_L', 'g_L', 'C_m', 'tau_ex', 'tau_in', 'E_Na', 'g_Na', 'E_K', 'g_K', 'Act_m', 'Act_h', 'Inact_n', 'I_e']),
    "iaf_cond_alpha": (
        [],
        [ 'V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e']),
    "iaf_neuron": (
        [],
        ['V_m', 'E_L', 'C_m', 'tau_m', 't_ref', 'V_th', 'V_reset', 'tau_syn', 'I_e']),
    "iaf_psc_alpha": (
        [],
        ['V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e']),
    "parrot": (
        [],
        []),
    "ac_generator": (
        [],
        ['amplitude', 'frequency', 'offset', 'phase']),
    "dc_generator": (
        ['amplitude'],
        []),
    "noise_generator": (
        ['mean'], 
        ['std', 'dt', 'start', 'stop']),
    "poisson_generator": (
        ['rate'],
        ['start', 'stop']),
    "smp_generator": (
        [],
        ['dc', 'ac', 'freq', 'phi']),
    "spike_generator": (
        ['spike_times'],
        ['start', 'stop', 'step']),  
    }