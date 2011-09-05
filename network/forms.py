# -*- coding: utf-8 -*-
from django import forms
from form_utils.forms import BetterForm, BetterModelForm # They are able to group fields in fieldsets.

from network.models import Network
from network.helpers import values_extend

import numpy as np

__all__ = ["NetworkForm", 
          "HhPscAlphaForm", "IafCondAlphaForm", "IafNeuronForm", "IafPscAlphaForm", 
          "ACGeneratorForm", "DCGeneratorForm", "NoiseGeneratorForm", "PoissonGeneratorForm", "SmpGeneratorForm", "SpikeGeneratorForm",
          "SpikeDetectorForm", "VoltmeterForm"]

class NetworkForm(BetterModelForm):
    """
    Form for network object
    """
    
    duration = forms.FloatField(help_text="Enter value, which is divisible by 50.")
    seed = forms.IntegerField(required=False, help_text="Enter only positive value.")  
    resolution = forms.FloatField(required=False,)
    
    def as_div(self):
        return self._html_output(u'<div class="field-wrapper" title="%(help_text)s">%(label)s %(errors)s %(field)s</div>', u'%s', '</div>', u'%s', False)
        
    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        
        # duration value should be divisible by 50, it's because of the visualization with protovis.
        # TODO: find a better code for protovis.
        if float(duration) % 50 != 0.0:
            raise forms.ValidationError('This value isn`t divisible by 50.')
        return duration

    class Meta:
        model = Network
        fieldsets = (('main', {'fields': ['duration']}),
                    ('Advanced', {'fields': ['seed', 'resolution'], 'classes': ['advanced', 'collapse']}))

class DeviceForm(BetterForm):
    """
    Parent form for input and neuron devices.
    """    
    
    def __init__(self, network_obj=None, *args, **kwargs):
        self.instance = network_obj
        super(DeviceForm, self).__init__(*args, **kwargs)
    
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    targets = forms.CharField(max_length=1000, required=False, help_text="Enter only ID of neurons, e.g. '1,2,4' or '1-3'")
    weight = forms.CharField(max_length=1000, required=False, initial=1.0, label='Weight (pA)', help_text="Enter either positive or negative values.")
    delay = forms.CharField(max_length=1000, required=False, initial=1.0, label='Delay (ms)', help_text="Enter only positive values is lower than 10 seconds.")

    def as_div(self):
        return self._html_output(u'<div class="field-wrapper" title="%(help_text)s">%(label)s %(errors)s %(field)s</div>', u'%s', '</div>', u'%s', False)

    def clean_targets(self):
        targets = self.cleaned_data.get('targets')

        if targets:
            
            # Extend targets, e.g. from 1-3 to 1,2,3
            try:
                extended_list = values_extend(targets, unique=True)
            except:
                raise forms.ValidationError('enter only number.')
            
            # Check if all targets are neurons
    
            for target in extended_list:
                neuron_ids = self.instance.neuron_ids()
                if not target in neuron_ids:
                    raise forms.ValidationError('targets should be neurons')
            
        return targets

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight:
            weights = weight.split(',')

            try:
                weights = np.array([float(val) for val in weights])
            except:
                raise forms.ValidationError('enter only number')

            # all weight values of that device are either positive or negative.
            negative_weights, positive_weights = weights < 0, weights >= 0
            if not negative_weights.all() and not positive_weights.all():
                raise forms.ValidationError('use either positive or negative values')
            
        return weight
        
    def clean_delay(self):
        delay = self.cleaned_data.get('delay')
        if delay:
            delays = delay.split(',')

            try:
                delays = np.array([float(val) for val in delays])
            except:
                raise forms.ValidationError('enter only numbers')
            
            # delay shouldn't be negative.
            negative_delays = delays < 0
            if negative_delays.any():
                raise forms.ValidationError('use only positive values')
            
            # delay shouldn't be more than 10s.
            if max(delays) > 10.0:
                raise forms.ValidationError('delay is too high')
            
        return delay


""" 
Neurons as child forms of DeviceForm 
"""

class HhPscAlphaForm(DeviceForm):
    V_m = forms.FloatField(required=False, label='Membrane potential (mV)')
    E_L = forms.FloatField(required=False, label='Resting membrane potential (mV)')
    g_L = forms.FloatField(required=False, label='Leak conductance (nS)')
    C_m = forms.FloatField(required=False, label='Capacity of the membrane (pF)')
    tau_ex = forms.FloatField(required=False, label='Rise time of the excitatory synaptic alpha function (ms)')
    tau_in = forms.FloatField(required=False, label='Rise time of the inhibitory synaptic alpha function (ms)')
    E_Na = forms.FloatField(required=False, label='Sodium reversal potential (mV)')
    g_Na = forms.FloatField(required=False, label='Sodium peak conductance (nS)')
    E_K = forms.FloatField(required=False, label='Potassium reversal potential (mV)')
    g_K = forms.FloatField(required=False, label='Potassium peak conductance (nS)')
    Act_m = forms.FloatField(required=False, label='Activation variable m')
    Act_h = forms.FloatField(required=False, label='Activation variable h')
    Inact_n = forms.FloatField(required=False, label='Inactivation variable n')      
    I_e = forms.FloatField(required=False, label='Constant external input current (pA)')

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay']}),
                    ('Advanced', {
                        'fields': ['V_m', 'E_L', 'g_L', 'C_m', 'tau_ex', 'tau_in', 'E_Na', 'g_Na', 'E_K', 'g_K', 'Act_m', 'Act_h', 'Inact_n', 'I_e'], 
                        'classes': ['advanced', 'collapse']}))
        row_attrs = {'model': {'is_hidden': True}}

class IafCondAlphaForm(DeviceForm):
    V_m = forms.FloatField(required=False, label='Membrane potential (mV)')
    E_L = forms.FloatField(required=False, label='Leak reversal potential (mV)')
    C_m = forms.FloatField(required=False, label='Capacity of the membrane (pF)')
    t_ref = forms.FloatField(required=False, label='Duration of refractory period (ms)')
    V_th = forms.FloatField(required=False, label='Spike threshold (mV)')
    V_reset = forms.FloatField(required=False, label='Reset Potential of the membrane (mV)')
    E_ex = forms.FloatField(required=False, label='Excitatory reversal potential (mV)')
    E_in = forms.FloatField(required=False, label='Inhibitory reversal potential (mV)')
    g_L = forms.FloatField(required=False, label='Leak conductance (nS)')
    tau_syn_ex = forms.FloatField(required=False, label='Rise time of the excitatory synaptic alpha function (ms)')
    tau_syn_in = forms.FloatField(required=False, label='Rise time of the inhibitory synaptic alpha function (ms)')
    I_e = forms.FloatField(required=False, label='Constant input current (pA)')

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay']}),
                    ('Advanced', {
                        'fields': ['V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e'], 
                        'classes': ['advanced', 'collapse']}))
        row_attrs = {'model': {'is_hidden': True}}

class IafNeuronForm(DeviceForm):
    V_m = forms.FloatField(required=False, label='Membrane potential (mV)')
    E_L = forms.FloatField(required=False, label='Resting membrane potential (mV)')
    C_m = forms.FloatField(required=False, label='Capacity of the membrane (pF)')
    tau_m = forms.FloatField(required=False, label='Membrane time constant (ms)')
    t_ref = forms.FloatField(required=False, label='Duration of refractory period (ms)')
    V_th = forms.FloatField(required=False, label='Spike threshold (mV)')
    V_reset = forms.FloatField(required=False, label='Reset Potential of the membrane (mV)')
    tau_syn = forms.FloatField(required=False, label='Rise time of the excitatory synaptic alpha function (ms)')
    I_e = forms.FloatField(required=False, label='Constant external input current (pA)')

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay']}),
                    ('Advanced', {
                        'fields': ['V_m', 'E_L', 'C_m', 'tau_m', 't_ref', 'V_th', 'V_reset', 'tau_syn', 'I_e'], 
                        'classes': ['advanced', 'collapse']}))
        row_attrs = {'model': {'is_hidden': True}}
        
class IafPscAlphaForm(DeviceForm):
    V_m = forms.FloatField(required=False, label='Membrane potential (mV)')
    E_L = forms.FloatField(required=False, label='Leak reversal potential (mV)')
    C_m = forms.FloatField(required=False, label='Capacity of the membrane (pF)')
    t_ref = forms.FloatField(required=False, label='Duration of refractory period (ms)')
    V_th = forms.FloatField(required=False, label='Spike threshold (mV)')
    V_reset = forms.FloatField(required=False, label='Reset Potential of the membrane (mV)')
    E_ex = forms.FloatField(required=False, label='Excitatory reversal potential (mV)')
    E_in = forms.FloatField(required=False, label='Inhibitory reversal potential (mV)')
    g_L = forms.FloatField(required=False, label='Leak conductance (nS)')
    tau_syn_ex = forms.FloatField(required=False, label='Rise time of the excitatory synaptic alpha function (ms)')
    tau_syn_in = forms.FloatField(required=False, label='Rise time of the inhibitory synaptic alpha function (ms)')
    I_e = forms.FloatField(required=False, label='Constant input current (pA)')

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay']}),
                    ('Advanced', {
                        'fields': ['V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e'], 
                        'classes': ['advanced', 'collapse']}))
        row_attrs = {'model': {'is_hidden': True}}


""" 
Inputs as child forms of DeviceForm
"""

class ACGeneratorForm(DeviceForm):
    amplitude = forms.FloatField(required=False, label='Amplitude of sine current (pA)')
    offset = forms.FloatField(required=False, label='Constant amplitude offset (pA)')
    phase = forms.FloatField(required=False, label='Phase of sine current (0-360 deg)')
    frequency = forms.FloatField(required=False, label='Frequency (Hz)')

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay']}),
                    ('Advanced', {'fields': ['amplitude', 'offset', 'phase', 'frequency'], 'classes': ['advanced', 'collapse']}))
        row_attrs = {'model': {'is_hidden': True}}

class DCGeneratorForm(DeviceForm):
    amplitude = forms.FloatField(required=False, label='Amplitude of current (pA)')

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay']}),
                    ('Advanced', {'fields': ['amplitude'], 'classes': ['advanced', 'collapse']}))
        row_attrs = {'model': {'is_hidden': True}}

class NoiseGeneratorForm(DeviceForm):
    mean = forms.FloatField(required=False, label='Mean value of the noise current (pA)')
    std = forms.FloatField(required=False, label='Standard deviation of noise current (pA)')
    dt = forms.FloatField(required=False, label='Interval between changes in current (ms)')
    start = forms.FloatField(required=False, label='Start (ms)')
    stop = forms.FloatField(required=False, label='Stop (ms)')

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay']}),
                    ('Advanced', {'fields': ['mean', 'std', 'dt', 'start', 'stop'], 'classes': ['advanced', 'collapse']}))
        row_attrs = {'model': {'is_hidden': True}}

class PoissonGeneratorForm(DeviceForm):
    rate = forms.FloatField(required=False, label='Mean firing rate (Hz)')
    origin = forms.FloatField(required=False, label='Time origin for device timer (ms)')
    start = forms.FloatField(required=False, label='Begin of device application with resp. to origin (ms)')
    stop = forms.FloatField(required=False, label='End of device application with resp. to origin (ms)')

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay', 'rate']}),
                    ('Advanced', {'fields': ['origin', 'start', 'stop'], 'classes': ['advanced', 'collapse']}))
        row_attrs = {'model': {'is_hidden': True}}

class SmpGeneratorForm(DeviceForm):
    dc = forms.FloatField(required=False, label='Mean firing rate (spikes/second)')
    ac = forms.FloatField(required=False, label='Firing rate modulation amplitude (spikes/second)')
    freq = forms.FloatField(required=False, label='Modulation frequency (Hz)')
    phi = forms.FloatField(required=False, label='Modulation phase (radian)')

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay']}),
                    ('Advanced', {'fields': ['dc', 'ac', 'freq', 'phi'], 'classes': ['advanced', 'collapse']}))
        row_attrs = {'model': {'is_hidden': True}}

class SpikeGeneratorForm(DeviceForm):
    origin = forms.FloatField(required=False, label='Time origin for device timer (ms)')
    start = forms.FloatField(required=False, label='Earliest possible time stamp of a spike to be emitted (ms)')
    stop = forms.FloatField(required=False, label='Earliest time stamp of a potential spike event that is not emitted (ms)')
    spike_times = forms.CharField(max_length=1000, required=False, label='Spike-times (ms)')
    spike_weights = forms.CharField(max_length=1000, required=False, label='Corrsponding spike-weights, the unit depends on the receiver.')

    def clean_spike_times(self):
        spike_times = self.cleaned_data.get('spike_times')
        if spike_times:
            spike_times_list = spike_times.split(',')

            try:
                spike_time_list = np.array([float(val) for val in spike_times_list])
            except:
                raise forms.ValidationError('enter only numbers')
            
        return spike_times
        
    def clean_spike_weights(self):
        spike_weights = self.cleaned_data.get('spike_weights')
        if spike_weights:
            spike_weights_list = spike_weights.split(',')

            try:
                spike_weights_list = np.array([float(val) for val in spike_weights_list])
            except:
                raise forms.ValidationError('enter only numbers')
            
        return spike_weights    

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay']}),
                    ('Advanced', {'fields': ['start', 'stop', 'spike_times', 'spike_weights'], 'classes': ['advanced', 'collapse']}))
        row_attrs = {'model': {'is_hidden': True}}


""" 
Outputs as entire forms 
"""

class SpikeDetectorForm(BetterForm):
    def __init__(self, network_obj=None, *args, **kwargs):
        self.instance = network_obj
        super(SpikeDetectorForm, self).__init__(*args, **kwargs)
        
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    sources = forms.CharField(max_length=1000, help_text="Enter only ID of neurons, e.g. '1,2,4' or '1-3'")

    def as_div(self):
        return self._html_output(u'<div class="field-wrapper" title="%(help_text)s">%(label)s %(errors)s %(field)s</div>', u'%s', '</div>', u'%s', False)

    def clean_sources(self):
        sources = self.cleaned_data.get('sources').replace(' ','')
        try:
            extended_list = values_extend(sources, unique=True)
        except:
            raise forms.ValidationError('enter only number.')
        
        # check if all sources are neurons
        neuron_ids = self.instance.neuron_ids()
        for source in extended_list:
            if not source in neuron_ids:
                raise forms.ValidationError('sources should be neurons')
            
        return sources
        
class VoltmeterForm(BetterForm):
    def __init__(self, network_obj=None, *args, **kwargs):
        self.instance = network_obj
        super(VoltmeterForm, self).__init__(*args, **kwargs)
        
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    targets = forms.CharField(max_length=1000, help_text="Enter only ID of neurons, e.g. '1,2,4' or '1-3'")


    def as_div(self):
        return self._html_output(u'<div class="field-wrapper" title="%(help_text)s">%(label)s %(errors)s %(field)s</div>', u'%s', '</div>', u'%s', False)

    def clean_targets(self):
        targets = self.cleaned_data.get('targets').replace(' ','')
        try:
            extended_list = values_extend(targets, unique=True, toString=True)
        except:
            raise forms.ValidationError('enter only number.')
        
        # check if all targets are neurons
        neuron_ids = self.instance.neuron_ids()        
        for target in extended_list:
            if not int(target) in neuron_ids:
                raise forms.ValidationError('targets should be neurons')
            
        return targets
    
