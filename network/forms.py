# -*- coding: utf-8 -*-
from django import forms

import lib.json as json
from network.models import Network

__all__ = ["NetworkForm", "LinkForm", "NodesCSVForm", "NodeForm"]

class NetworkForm(forms.ModelForm):
    """ Form for network object """
    duration = forms.FloatField(required=True,
        label = 'Duration (ms)',
        help_text = "The length of simulation time",
        widget = forms.TextInput(attrs = {
            'placeholder': 'duration',
            'class': 'required limit min 1000 max 10000'}))
    same_seed = forms.BooleanField(required=False, initial=True)
    overwrite = forms.BooleanField(required=False, label = 'Overwrite version')
    nodes = forms.CharField(max_length=10000, widget=forms.HiddenInput())
    links = forms.CharField(max_length=10000, widget=forms.HiddenInput())

    class Meta:
        model = Network
        fields = ('duration', 'same_seed', 'overwrite')


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
            ('voltmeter', 'Voltmeter'),
            ('spike_detector', 'Spike Detector'),
            ('hh_psc_alpha', 'HH PSC Alpha'),
            ('iaf_cond_alpha', 'IAF Cond Alpha'),
            ('iaf_neuron', 'IAF Neuron'),
            ('iaf_psc_alpha', 'IAF PSC Alpha'),
            ('ac_generator', 'AC Generator'),
            ('dc_generator', 'DC Generator'),
            ('noise_generator', 'Noise Generator'),
            ('poisson_generator', 'Poisson Generator'),
            ('spike_generator', 'Spike Generator')])

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
        label = 'Rise time of the exc. synaptic alpha function (ms)',
#        help_text = '',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'tau_syn',
            'placeholder': '2.0',
            'class': 'neuron iaf_neuron'}))
    tau_syn_ex = forms.FloatField(required = False,
#        initial = .2,
        label = 'Rise time of the exc. synaptic alpha function (ms)',
#        help_text='',
        widget = forms.TextInput(attrs = {
#            'placeholder': 'tau_syn_ex',
            'placeholder': '0.2',
            'class': 'neuron iaf_cond_alpha iaf_psc_alpha'}))
    tau_syn_in = forms.FloatField(required = False,
#        initial = 2.,
        label = 'Rise time of the inh. synaptic alpha function (ms)',
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




"""
Outdated
"""


import numpy as np
from form_utils.forms import BetterForm, BetterModelForm # They are able to group fields in fieldsets.
from network.helpers import values_extend
from network.network_settings import PARAMS_ORDER

__all__  += ["NetworkLabelForm", "DeviceCSVForm", "UploadFileForm",
          "HhPscAlphaForm", "IafCondAlphaForm", "IafNeuronForm", "IafPscAlphaForm", 'ParrotForm',
          "ACGeneratorForm", "DCGeneratorForm", "NoiseGeneratorForm", "PoissonGeneratorForm", "SmpGeneratorForm", "SpikeGeneratorForm",
          "SpikeDetectorForm", "VoltmeterForm"]

class NetworkLabelForm(forms.ModelForm):
    
    class Meta:
        model = Network
        fields = ('label',)

    def as_div(self):
        return self._html_output(u'<div class="fieldWrapper">%(label)s %(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'%s', False)


class DeviceCSVForm(forms.Form):
    csv = forms.CharField(max_length=1000, required=False, widget=forms.Textarea, 
          help_text='Enter values in correct order, seperated by semicolon. e.g. [model]; [ID]; [targets/sources]; [weight]; [delay]; [optional params]')

    def as_div(self):
        return self._html_output(u'<div class="fieldWrapper">%(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'%s', False)


class UploadFileForm(forms.Form):
    file  = forms.FileField()

    def as_div(self):
        return self._html_output(u'<div class="fieldWrapper">%(label)s %(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'%s', False)


class NeuronForm(BetterForm):
    """ Parent form for input and neuron devices """    
    def __init__(self, network_obj=None, *args, **kwargs):
        self.instance = network_obj
        if args:
            self.neuron_ids = json.decode(str(args[0]['neuron_ids']))
        super(NeuronForm, self).__init__(*args, **kwargs)

    id = forms.IntegerField(widget=forms.HiddenInput())
    type = forms.CharField(max_length=32, widget=forms.HiddenInput(), initial='neuron')
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    label = forms.CharField(max_length=32, required=False, widget=forms.HiddenInput())
    targets = forms.CharField(max_length=1000, required=False, help_text="Enter neuron id(s), e.g. '1,2,3' or '1-4'")
    weight = forms.CharField(max_length=1000, required=False, initial=1.0, label='Weight (pA)', help_text="Enter either positive or negative values.")
    delay = forms.CharField(max_length=1000, required=False, initial=1.0, label='Delay (ms)', help_text="Enter positive values < 10ms.")
    #synapse_type = forms.ChoiceField(choices=(('static_synapse', 'static synapse'),('tsodyks_synapse', 'tsodyks synapse')), help_text='')

    def clean_targets(self):
        targets = self.cleaned_data.get('targets')

        if targets:
            # Extend targets, e.g. from 1-3 to 1,2,3
            try:
                extended_list = values_extend(targets, unique=True)
            except:
                raise forms.ValidationError("Enter neuron id(s) in correct order, e.g. '1,2,3' or '1-4'")
            
            # Check if all targets are neurons
            for target in extended_list:
                neuron_ids = self.instance.neuron_ids()
                if not (target in neuron_ids or target in self.neuron_ids):
                    raise forms.ValidationError('Targets should be neurons.')
            
        return targets

    def clean_weight(self):
        targets = self.cleaned_data.get('targets')
        if targets:
            weight = self.cleaned_data.get('weight')
            if weight:
                weights = weight.split(',')

                try:
                    weights = np.array(weights, dtype=float)
                except:
                    raise forms.ValidationError('Enter either positive or negative values.')

                # all weight values of that device are either positive or negative.
                negative_weights, positive_weights = weights < 0, weights >= 0
                if not negative_weights.all() and not positive_weights.all():
                    raise forms.ValidationError('Enter either positive or negative values.')
            return weight
        return u''
        
    def clean_delay(self):
        targets = self.cleaned_data.get('targets')
        if targets:
            delay = self.cleaned_data.get('delay')
            if delay:
                delays = delay.split(',')

                try:
                    delays = np.array(delays, dtype=float)
                    
                    # delay shouldn't be negative.
                    assert min(delays) >= 0
                
                    # delay shouldn't be more than 10s.
                    assert max(delays) <= 10.0
                except:
                    raise forms.ValidationError('Enter positive values < 10ms.')
                
            return delay
        return u''

""" 
Neurons as child forms of DeviceForm 
"""

class HhPscAlphaForm(NeuronForm):
    V_m = forms.FloatField(required=False, initial=-65., label='Membrane potential (mV)', help_text='')
    E_L = forms.FloatField(required=False, initial=-54.4, label='Resting membrane potential (mV)', help_text='')
    g_L = forms.FloatField(required=False, initial=30., label='Leak conductance (nS)', help_text='')
    C_m = forms.FloatField(required=False, initial=100., label='Capacity of the membrane (pF)', help_text='')
    E_Na = forms.FloatField(required=False, initial=50., label='Sodium reversal potential (mV)', help_text='')
    g_Na = forms.FloatField(required=False, initial=12000., label='Sodium peak conductance (nS)', help_text='')
    E_K = forms.FloatField(required=False, initial=-77., label='Potassium reversal potential (mV)', help_text='')
    g_K = forms.FloatField(required=False, initial=3600., label='Potassium peak conductance (nS)', help_text='')
    I_e = forms.FloatField(required=False, initial=0., label='Constant external input current (pA)', help_text='')

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['hh_psc_alpha'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['hh_psc_alpha'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class IafCondAlphaForm(NeuronForm):
    V_m = forms.FloatField(required=False, initial=-70., label='Membrane potential (mV)', help_text='')
    E_L = forms.FloatField(required=False, initial=-70., label='Leak reversal potential (mV)', help_text='')
    C_m = forms.FloatField(required=False, initial=250., label='Capacity of the membrane (pF)', help_text='')
    t_ref = forms.FloatField(required=False, initial=2., label='Duration of refractory period (ms)', help_text='')
    V_th = forms.FloatField(required=False, initial=-55., label='Spike threshold (mV)', help_text='')
    V_reset = forms.FloatField(required=False, initial=-60., label='Reset Potential of the membrane (mV)', help_text='')
    E_ex = forms.FloatField(required=False, initial=0., label='Excitatory reversal potential (mV)', help_text='')
    E_in = forms.FloatField(required=False, initial=-85., label='Inhibitory reversal potential (mV)', help_text='')
    g_L = forms.FloatField(required=False, initial=16.7, label='Leak conductance (nS)', help_text='')
    tau_syn_ex = forms.FloatField(required=False, initial=.2, label='Rise time of the exc. synaptic alpha function (ms)', help_text='')
    tau_syn_in = forms.FloatField(required=False, initial=2., label='Rise time of the inh. synaptic alpha function (ms)', help_text='')
    I_e = forms.FloatField(required=False, initial=0., label='Constant input current (pA)', help_text='')

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['iaf_cond_alpha'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['iaf_cond_alpha'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class IafNeuronForm(NeuronForm):
    V_m = forms.FloatField(required=False, initial=-70., label='Membrane potential (mV)', help_text='')
    E_L = forms.FloatField(required=False, initial=-70., label='Resting membrane potential (mV)', help_text='')
    C_m = forms.FloatField(required=False, initial=250., label='Capacity of the membrane (pF)', help_text='')
    tau_m = forms.FloatField(required=False, initial=10., label='Membrane time constant (ms)', help_text='')
    t_ref = forms.FloatField(required=False, initial=2., label='Duration of refractory period (ms)', help_text='')
    V_th = forms.FloatField(required=False, initial=-55., label='Spike threshold (mV)', help_text='')
    V_reset = forms.FloatField(required=False, initial=-70., label='Reset Potential of the membrane (mV)', help_text='')
    tau_syn = forms.FloatField(required=False, initial=2., label='Rise time of the exc. synaptic alpha function (ms)', help_text='')
    I_e = forms.FloatField(required=False, initial=0., label='Constant external input current (pA)', help_text='')

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['iaf_neuron'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['iaf_neuron'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}
        
class IafPscAlphaForm(NeuronForm):
    V_m = forms.FloatField(required=False, initial=-70., label='Membrane potential (mV)', help_text='')
    E_L = forms.FloatField(required=False, initial=-70., label='Leak reversal potential (mV)', help_text='')
    C_m = forms.FloatField(required=False, initial=250., label='Capacity of the membrane (pF)', help_text='')
    t_ref = forms.FloatField(required=False, initial=2., label='Duration of refractory period (ms)', help_text='')
    V_th = forms.FloatField(required=False, initial=-55., label='Spike threshold (mV)', help_text='')
    V_reset = forms.FloatField(required=False, initial=-70., label='Reset Potential of the membrane (mV)', help_text='')
    tau_syn_ex = forms.FloatField(required=False, initial=2., label='Rise time of the exc. synaptic alpha function (ms)', help_text='')
    tau_syn_in = forms.FloatField(required=False, initial=2., label='Rise time of the inh. synaptic alpha function (ms)', help_text='')
    I_e = forms.FloatField(required=False, initial=0., label='Constant input current (pA)', help_text='')

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['iaf_psc_alpha'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['iaf_psc_alpha'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class ParrotForm(NeuronForm):
  
     class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['parrot'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['parrot'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

""" 
Inputs as child forms of DeviceForm
"""

class DeviceForm(BetterForm):
    """ Parent form for input and neuron devices """    
    def __init__(self, network_obj=None, *args, **kwargs):
        self.instance = network_obj
        if args:
            self.neuron_ids = json.decode(str(args[0]['neuron_ids']))
        super(DeviceForm, self).__init__(*args, **kwargs)

    id = forms.IntegerField(widget=forms.HiddenInput())
    type = forms.CharField(max_length=32, widget=forms.HiddenInput(), initial='input')
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    label = forms.CharField(max_length=32, required=False, widget=forms.HiddenInput())
    targets = forms.CharField(max_length=1000, help_text="Enter neuron id(s), e.g. '1,2,3' or '1-4'", widget=forms.TextInput(attrs={'placeholder': "Targets"}))
    weight = forms.CharField(max_length=1000, initial=1.0, label='Weight (pA)', help_text="Enter either positive or negative values.", widget=forms.TextInput(attrs={'placeholder':'Weight'}))
    delay = forms.CharField(max_length=1000, initial=1.0, label='Delay (ms)', help_text="Enter positive values < 10ms.", widget=forms.TextInput(attrs={'placeholder':'Delay'}))
    #synapse_type = forms.ChoiceField(choices=(('static_synapse', 'static synapse'),('tsodyks_synapse', 'tsodyks synapse')), help_text='')

    def clean_targets(self):
        targets = self.cleaned_data.get('targets')

        if targets:
            # Extend targets, e.g. from 1-3 to 1,2,3
            try:
                extended_list = values_extend(targets, unique=True)
            except:
                raise forms.ValidationError("Enter neuron id(s) in correct order, e.g. '1,2,3' or '1-4'")
            
            # Check if all targets are neurons
            for target in extended_list:
                neuron_ids = self.instance.neuron_ids()
                if not (target in neuron_ids or target in self.neuron_ids):
                    raise forms.ValidationError('Targets should be neurons.')
            
        return targets

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight:
            weights = weight.split(',')

            try:
                weights = np.array(weights, dtype=float)
            except:
                raise forms.ValidationError('Enter either positive or negative values.')

            # all weight values of that device are either positive or negative.
            negative_weights, positive_weights = weights < 0, weights >= 0
            if not negative_weights.all() and not positive_weights.all():
                raise forms.ValidationError('Enter either positive or negative values.')
            
        return weight
        
    def clean_delay(self):
        delay = self.cleaned_data.get('delay')
        if delay:
            delays = delay.split(',')

            try:
                delays = np.array(delays, dtype=float)
                
                # delay shouldn't be negative.
                assert min(delays) >= 0
            
                # delay shouldn't be more than 10s.
                assert max(delays) <= 10.0
            except:
                raise forms.ValidationError('Enter positive values < 10ms.')
            
        return delay

class ACGeneratorForm(DeviceForm):
    amplitude = forms.FloatField(required=False, initial=0., label='Amplitude (pA)', help_text='Enter only values > 0.')
    frequency = forms.FloatField(required=False, initial=0., label='Frequency (Hz)', help_text='Enter only positive values.')
    offset = forms.FloatField(required=False, label='Constant amplitude (pA)', help_text='')
    phase = forms.FloatField(required=False, label='Phase (0-360 deg)', help_text='Enter only values between 0 and 360.')


    def clean_amplitude(self):
        amplitude = self.cleaned_data.get('amplitude')
        if amplitude:
            try:
                # amplitude shouldn't be negative or zero.
                assert float(amplitude) > 0
            
            except:
                raise forms.ValidationError('Enter only values > 0.')
            
        return amplitude

    def clean_frequency(self):
        frequency = self.cleaned_data.get('frequency')
        if frequency:
            try:
                # frequency shouldn't be negative.
                assert float(frequency) >= 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
            
        return frequency

    def clean_phase(self):
        phase = self.cleaned_data.get('phase')
        if phase:
            try:
                # phase shouldn't be negative.
                assert float(phase) >= 0

                # phase shouldn't be greater than 360.
                assert float(phase) <= 360

            except:
                raise forms.ValidationError('Enter only between 0 and 360.')
            
        return phase

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['ac_generator'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['ac_generator'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class DCGeneratorForm(DeviceForm):
    amplitude = forms.FloatField(label='Amplitude (pA)', help_text='')

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['dc_generator'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['dc_generator'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class NoiseGeneratorForm(DeviceForm):
    mean = forms.FloatField(required=False, label='Mean value (pA)', help_text='')
    std = forms.FloatField(required=False, label='Standard deviation (pA)', help_text='Enter only positive values.')
    dt = forms.FloatField(required=False, label='Time steps (ms)', help_text='Enter only values > 0.')
    start = forms.FloatField(required=False, label='Start (ms)', help_text='Enter only positive values.')
    stop = forms.FloatField(required=False, label='Stop (ms)', help_text='Enter only values > 0.')

    def clean_std(self):
        std = self.cleaned_data.get('std')
        if std:
            try:
                # std shouldn't be negative.
                assert float(std) >= 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
            
        return std
        
    def clean_dt(self):
        dt = self.cleaned_data.get('dt')
        if dt:
            try:
                # dt shouldn't be negative or zero.
                assert float(dt) > 0
            
            except:
                raise forms.ValidationError('Enter only values > 0.')
            
        return dt

    def clean_start(self):
        start = self.cleaned_data.get('start')
        if start:
            try:
                # start shouldn't be negative.
                assert float(start) >= 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
            
        return start
        
    def clean_stop(self):
        stop = self.cleaned_data.get('stop')
        if stop:
            try:
                # stop shouldn't be negative or zero.
                assert float(stop) > 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
            
        return stop

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['noise_generator'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['noise_generator'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class PoissonGeneratorForm(DeviceForm):
    rate = forms.FloatField(label='Mean firing rate (Hz)', help_text='Enter only positive values.')
    #origin = forms.FloatField(required=False, label='Time origin for device timer (ms)', help_text='')
    start = forms.FloatField(required=False, label='Start (ms)', help_text='Enter only positive values.')
    stop = forms.FloatField(required=False, label='Stop (ms)', help_text='Enter only positive values.')

    def clean_rate(self):
        rate = self.cleaned_data.get('rate')
        if rate:
            try:
                # rate shouldn't be negative or zero.
                assert float(rate) > 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
            
        return rate

    def clean_start(self):
        start = self.cleaned_data.get('start')
        if start:
            try:
                # start shouldn't be negative.
                assert float(start) >= 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
            
        return start
        
    def clean_stop(self):
        stop = self.cleaned_data.get('stop')
        if stop:
            try:
                # stop shouldn't be negative or zero.
                assert float(stop) > 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
            
        return stop

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['poisson_generator'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['poisson_generator'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class SmpGeneratorForm(DeviceForm):
    dc = forms.FloatField(required=False, label='Mean firing rate (spikes/second)', help_text='')
    ac = forms.FloatField(required=False, label='Firing rate modulation amplitude (spikes/second)', help_text='')
    freq = forms.FloatField(required=False, label='Modulation frequency (Hz)', help_text='Enter only positive values.')
    phi = forms.FloatField(required=False, label='Modulation phase (radian)', help_text='')

    def clean_freq(self):
        freq = self.cleaned_data.get('freq')
        if freq:
            try:
                # freq shouldn't be negative or zero.
                assert float(freq) > 0
            
            except:
                raise forms.ValidationError('Enter positive values.')
            
        return freq

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['smp_generator'][0] , 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['smp_generator'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class SpikeGeneratorForm(DeviceForm):
    spike_times = forms.CharField(max_length=10000, label='Spike-times (ms)', help_text="Enter spike times manually (comma separated) or select start, end, step values")   
    start = forms.FloatField(required=False, initial=0, label='Start time (ms)', help_text='Enter only positive values.')
    stop = forms.FloatField(required=False, initial=np.inf, label='End time (ms)', help_text='Enter only positive values.')
    step = forms.FloatField(required=False, label='Step size (ms)', help_text='Enter only positive values.')

    def clean_spike_times(self):
        spike_times = self.cleaned_data.get('spike_times')

        if spike_times:
            spike_times_list = spike_times.split(',')

            try:
                spike_times_list = np.array(spike_times_list, dtype=float)
                
                # spike times shouldn't be negative.
                assert min(spike_times_list) >= 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
              
        return spike_times

    def clean_start(self):
        start = self.cleaned_data.get('start')
        if start:
            try:
                # start shouldn't be negative.
                assert float(start) >= 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
            
        return start
        
    def clean_stop(self):
        stop = self.cleaned_data.get('stop')
        if stop:
            try:
                # stop shouldn't be negative or zero.
                assert float(stop) > 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
        
        if stop == np.inf:
            return
        return stop
              
    def clean_step(self):
        step = self.cleaned_data.get('step')
        if step:
            try:
                # step shouldn't be negative or zero.
                assert float(step) > 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')

        return step
        
    class Meta:
        fieldsets = (('main', {'fields': ['label'] + PARAMS_ORDER['spike_generator'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['spike_generator'][1], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}


""" 
Output Forms
"""

class SpikeDetectorForm(BetterForm):
    def __init__(self, network_obj=None, *args, **kwargs):
        self.instance = network_obj
        if args:
            self.neuron_ids = json.decode(str(args[0]['neuron_ids']))
        super(SpikeDetectorForm, self).__init__(*args, **kwargs)
        
    id = forms.IntegerField(widget=forms.HiddenInput())  
    type = forms.CharField(max_length=32, widget=forms.HiddenInput(), initial='output')
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    label = forms.CharField(max_length=32, required=False, widget=forms.HiddenInput())
    sources = forms.CharField(max_length=1000, help_text="Enter neuron id(s), e.g. '1,2,3' or '1-4'")

    def clean_sources(self):
        sources = self.cleaned_data.get('sources').replace(' ','')
        try:
            extended_list = values_extend(sources, unique=True)
        except:
            raise forms.ValidationError("Enter neuron id(s), e.g. '1,2,3' or '1-4'")
        
        # check if all sources are neurons
        neuron_ids = self.instance.neuron_ids()
        parrot_ids = self.instance.neuron_ids(model='parrot_neuron')

        for source in extended_list:
            if not (source in neuron_ids or source in self.neuron_ids):
                raise forms.ValidationError("Sources should be neurons.")
            if source in parrot_ids:
                raise forms.ValidationError("Some of the sources are not recordable.")

        return sources

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['spike_detector'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['spike_detector'][1], 'classes': ['advanced']}))


class VoltmeterForm(BetterForm):
    def __init__(self, network_obj=None, *args, **kwargs):
        self.instance = network_obj
        if args:
            self.neuron_ids = json.decode(str(args[0]['neuron_ids']))
        super(VoltmeterForm, self).__init__(*args, **kwargs)

    id = forms.IntegerField(widget=forms.HiddenInput())
    type = forms.CharField(max_length=32, widget=forms.HiddenInput(), initial='output')
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    label = forms.CharField(max_length=32, required=False,  widget=forms.HiddenInput())
    targets = forms.CharField(max_length=1000, help_text="Enter neuron id(s), e.g. '1,2,3' or '1-4'")

    def clean_targets(self):
        targets = self.cleaned_data.get('targets').replace(' ','')
        try:
            extended_list = values_extend(targets, unique=True)
        except:
            raise forms.ValidationError("Enter neuron id(s), e.g. '1,2,3' or '1-4'")
        
        # check if all targets are neurons
        neuron_ids = self.instance.neuron_ids()
        parrot_ids = self.instance.neuron_ids(model='parrot_neuron')
        
        for target in extended_list:
            if not (target in neuron_ids or target in self.neuron_ids):
                raise forms.ValidationError("Targets should be neurons.")
            if target in parrot_ids:
                raise forms.ValidationError("Some of the targets are not recordable.")
            
        return targets

    class Meta:
        fieldsets = (('main', {'fields': PARAMS_ORDER['voltmeter'][0], 'classes': ['required']}),
                    ('Advanced', {'fields': PARAMS_ORDER['voltmeter'][1], 'classes': ['advanced']}))

