# -*- coding: utf-8 -*-
from django import forms

import lib.json as json
from network.models import Network


class NetworkForm(forms.ModelForm):
    """ Form for network object """

    duration = forms.FloatField(required=True,
        label = 'Duration (ms)',
        help_text = "The length of simulation",
        widget = forms.TextInput(attrs = {
            'placeholder': 'duration',
            'class': 'required limit min 1000 max 5000'}))
    same_seed = forms.BooleanField(required=False, initial=True)
    overwrite = forms.BooleanField(required=False, label = 'Overwrite results')
    nodes = forms.CharField(max_length=10000, widget=forms.HiddenInput())
    links = forms.CharField(max_length=10000, widget=forms.HiddenInput())

    class Meta:
        model = Network
        fields = ('duration', 'same_seed', 'overwrite')

class NetworkCommentForm(forms.ModelForm):

    class Meta:
        model = Network
        fields = ('label', 'comment')

class LinkForm(forms.Form):
    weight = forms.FloatField(required = True, initial = 1., label = "Weight (pA)",
        widget = forms.TextInput(attrs = {'placeholder': '1'}))
    delay = forms.FloatField(required = True, initial = 1., label = "Delay (ms)",
        widget = forms.TextInput(attrs = {'placeholder': '1'}))


class NodesCSVForm(forms.Form):
    csv = forms.CharField(max_length=1000, required=False, widget=forms.Textarea, 
          help_text='Enter values in correct order, seperated by semicolon. e.g. [model]; [ID]; [optional params]')

    def as_div(self):
        return self._html_output(u'<div class="fieldWrapper">%(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'%s', False)


class NodeForm(forms.Form):
    model = forms.ChoiceField(required = True,
        label = 'Model',
        choices=[
            ('voltmeter', 'Voltmeter', 'output'), \
            ('spike_detector', 'Spike Detector', 'output'), \
            ('hh_psc_alpha', 'HH PSC Alpha', 'neuron'), \
            ('iaf_cond_alpha', 'IAF Cond Alpha', 'neuron'), \
            ('iaf_neuron', 'IAF Neuron', 'neuron'), \
            ('iaf_psc_alpha', 'IAF PSC Alpha', 'neuron'), \
            ('ac_generator', 'AC Generator', 'input'), \
            ('dc_generator', 'DC Generator', 'input'), \
            ('noise_generator', 'Noise Generator', 'input'), \
            ('poisson_generator', 'Poisson Generator', 'input'), \
            ('spike_generator', 'Spike Generator', 'input'), \
        ])

    V_m = forms.FloatField(required = False,
#        initial = -70.,
        label = 'Membrane potential (mV)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'V_m',
            'placeholder': '-70.0',
            'class': 'neuron hh_psc_alpha iaf_neuron iaf_cond_alpha iaf_psc_alpha'}))
    E_L = forms.FloatField(required = False,
#        initial = -70.,
        label = 'Resting membrane potential (mV)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'E_L',
            'placeholder': '-70.0',
           'class': 'neuron hh_psc_alpha iaf_neuron iaf_cond_alpha iaf_psc_alpha'}))
    g_L = forms.FloatField(required = False,
#        initial = 30.,
        label = 'Leak conductance (nS)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'g_L',
            'placeholder': '30.0',
            'class': 'neuron hh_psc_alpha'}))
    C_m = forms.FloatField(required = False,
#        initial = 250.,
        label = 'Capacity of the membrane (pF)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'C_m',
            'placeholder': '250.0',
            'class': 'neuron hh_psc_alpha iaf_neuron iaf_cond_alpha iaf_psc_alpha'}))
    E_Na = forms.FloatField(required = False,
#        initial = 50.,
        label = 'Sodium reversal potential (mV)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'E_Na',
            'placeholder': '50.0',
            'class': 'neuron hh_psc_alpha'}))
    g_Na = forms.FloatField(required = False,
#        initial = 12000.,
        label = 'Sodium peak conductance (nS)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'g_Na',
            'placeholder': '12000.0',
            'class': 'neuron hh_psc_alpha'}))
    E_K = forms.FloatField(required = False,
#        initial = -77.,
        label = 'Potassium reversal potential (mV)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'E_K',
            'placeholder': '-77.0',
            'class': 'neuron hh_psc_alpha'}))
    g_K = forms.FloatField(required = False,
#        initial = 3600.,
        label = 'Potassium peak conductance (nS)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'g_K',
            'placeholder': '3600.0',
            'class': 'neuron hh_psc_alpha'}))
    tau_m = forms.FloatField(required = False,
#        initial = 10.,
        label = 'Membrane time constant (ms)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'tau_m',
            'placeholder': '10.0',
            'class': 'positive nonzeroneuron iaf_neuron'}))
    t_ref = forms.FloatField(required = False,
#        initial = 2.,
        label = 'Duration of refractory period (ms)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 't_ref',
            'placeholder': '2.0',
            'class': 'positive nonzero neuron iaf_neuron iaf_cond_alpha iaf_psc_alpha'}))
    V_th = forms.FloatField(required = False,
#        initial = -55.,
        label = 'Spike threshold (mV)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'V_th',
            'placeholder': '-55.0',
            'class': 'neuron iaf_neuron iaf_cond_alpha iaf_psc_alpha'}))
    V_reset = forms.FloatField(required = False,
#        initial = -70.,
        label = 'Reset Potential of the membrane (mV)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'V_reset',
            'placeholder': '-70.0',
            'class': 'neuron iaf_neuron iaf_cond_alpha iaf_psc_alpha'}))
    E_ex = forms.FloatField(required = False,
#        initial = 0.,
        label = 'Excitatory reversal potential (mV)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'E_ex',
            'placeholder': '0.0',
            'class': 'neuron iaf_cond_alpha'}))
    E_in = forms.FloatField(required = False,
#        initial = -85.,
        label = 'Inhibitory reversal potential (mV)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'E_in',
            'placeholder': '-85.0',
            'class': 'neuron iaf_cond_alpha'}))
    tau_syn = forms.FloatField(required = False,
#        initial = 2.,
        label = 'Time constant of synapse (ms)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'tau_syn',
            'placeholder': '2.0',
            'class': 'neuron iaf_neuron'}))
    tau_syn_ex = forms.FloatField(required = False,
#        initial = .2,
        label = 'Time constant of excitatory synapse (ms)',
#        help_text='',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'tau_syn_ex',
            'placeholder': '0.2',
            'class': 'neuron iaf_cond_alpha iaf_psc_alpha'}))
    tau_syn_in = forms.FloatField(required = False,
#        initial = 2.,
        label = 'Time constant of inhibitory synapse (ms)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'tau_syn_in',
            'placeholder': '2.0',
            'class': 'neuron iaf_cond_alpha iaf_psc_alpha'}))
    I_e = forms.FloatField(required = False,
#        initial = 0.,
        label = 'Constant external input current (pA)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'I_e',
            'placeholder': '0.0',
            'class': 'neuron iaf_neuron iaf_cond_alpha iaf_psc_alpha'}))

    amplitude = forms.FloatField(required = True,
#        initial = 0.,
        label = 'Amplitude (pA)',
        help_text = 'Enter only values > 0.',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'amplitude',
            'placeholder': '0.0',
            'class': 'required positive input ac_generator dc_generator'}))
    frequency = forms.FloatField(required = False,
        label='Frequency (Hz)',
        help_text = 'Enter only positive values.',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'frequency',
            'placeholder': '0.0',
            'class': 'positive input ac_generator'}))
    phase = forms.FloatField(required=False,
        label='Phase (0-360 deg)',
        help_text='Enter only values between 0 and 360.',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'phase',
            'placeholder': '0.0',
            'class': 'positive limit max 360 input ac_generator'}))
    mean = forms.FloatField(required = False,
        label = 'Mean value (pA)',
        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'mean',
            'placeholder': '0.0',
            'class': 'positive input noise_generator'}))
    std = forms.FloatField(required = False,
        label = 'Standard deviation (pA)',
        help_text = 'Enter only positive values.',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'std',
            'placeholder': '0.0',
            'class': 'positive input noise_generator'}))
    dt = forms.FloatField(required = False,
        label = 'Time steps (ms)',
        help_text = 'Enter only values > 0.',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'dt',
            'placeholder': '1.0',
            'class': 'positive nonzero input noise_generator'}))
    rate = forms.FloatField(required = True,
        label = 'Mean firing rate (Hz)',
        help_text='Enter only positive values.',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'rate',
            'placeholder': '0.0',
            'class': 'required positive input poisson_generator'}))
    spike_times = forms.CharField(required = True,
        max_length = 10000, 
        label = 'Spike-times (ms)',
        help_text = "Enter spike times manually (comma separated) or select start, end, step values",
        widget = forms.TextInput(attrs = {
#            'placeholder': 'spike_times',
            'placeholder': '',
            'class': 'required positive input spike_generator'}))
    start = forms.FloatField(required = False,
#        initial = 0,
        label = 'Start time (ms)',
        help_text = 'Enter only positive values.',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'start',
            'placeholder': '0.0',
            'class': 'positive input poisson_generator spike_generator'}))
    stop = forms.FloatField(required = False,
#        initial = np.inf,
        label = 'End time (ms)',
        help_text = 'Enter only positive values.',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'stop',
            'placeholder': 'inf',
            'class': 'positive nonzero input poisson_generator spike_generator'}))
    step = forms.FloatField(required = False,
        label = 'Step size (ms)',
        help_text = 'Enter only positive values.',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'step',
            'placeholder': '',
            'class': 'positive input spike_generator'}))

