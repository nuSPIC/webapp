# -*- coding: utf-8 -*-
from django import forms
from form_utils.forms import BetterForm, BetterModelForm # They are able to group fields in fieldsets.

import lib.json as json
from network.models import Network
from network.helpers import values_extend

import numpy as np

__all__ = ["NetworkForm", 
          "HhPscAlphaForm", "IafCondAlphaForm", "IafNeuronForm", "IafPscAlphaForm", 'ParrotForm',
          "ACGeneratorForm", "DCGeneratorForm", "NoiseGeneratorForm", "PoissonGeneratorForm", "SmpGeneratorForm", "SpikeGeneratorForm",
          "SourceForm", "TargetForm"]

class NetworkForm(BetterModelForm):
    """ Form for network object """
    duration = forms.FloatField(help_text="Enter positive value.")
    same_seed = forms.BooleanField(required=False, initial=True)
    resolution = forms.FloatField(required=False, help_text='')
    
    class Meta:
        model = Network
        fieldsets = (('main', {'fields': ['duration', 'same_seed']}),
                    ('Advanced', {'fields': [], 'classes': ['advanced', 'collapse']}))

class NeuronForm(BetterForm):
    """ Parent form for input and neuron devices """    
    def __init__(self, network_obj=None, *args, **kwargs):
        self.instance = network_obj
        if args:
            self.neuron_ids = json.decode(str(args[0]['neuron_ids']))
        super(NeuronForm, self).__init__(*args, **kwargs)
    
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    targets = forms.CharField(max_length=1000, required=False,help_text="Enter neuron id(s), e.g. '1,2,3' or '1-4'")
    weight = forms.CharField(max_length=1000, required=False,initial=1.0, label='Weight (pA)', help_text="Enter either positive or negative values.")
    delay = forms.CharField(max_length=1000, required=False,initial=1.0, label='Delay (ms)', help_text="Enter positive values < 10ms.")
    #synapse_type = forms.ChoiceField(choices=(('static_synapse', 'static synapse'),('tsodyks_synapse', 'tsodyks synapse')), help_text='')

    def as_div(self):
        return self._html_output(u'<div class="field-wrapper" title="%(help_text)s">%(label)s %(errors)s %(field)s</div>', u'%s', '</div>', u'%s', False)

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
        fieldsets = (('main', {'fields': ['model'], 'classes': ['required']}),
                    ('Advanced', {
                        'fields': ['targets', 'weight', 'delay', 'V_m', 'E_L', 'g_L', 'C_m', 'tau_ex', 'tau_in', 'E_Na', 'g_Na', 'E_K', 'g_K', 'Act_m', 'Act_h', 'Inact_n', 'I_e'], 
                        'classes': ['advanced']}))
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
        fieldsets = (('main', {'fields': ['model'], 'classes': ['required']}),
                    ('Advanced', {
                        'fields': ['targets', 'weight', 'delay', 'V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e'], 
                        'classes': ['advanced']}))
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
        fieldsets = (('main', {'fields': ['model'], 'classes': ['required']}),
                    ('Advanced', {
                        'fields': ['targets', 'weight', 'delay', 'V_m', 'E_L', 'C_m', 'tau_m', 't_ref', 'V_th', 'V_reset', 'tau_syn', 'I_e'], 
                        'classes': ['advanced']}))
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
        fieldsets = (('main', {'fields': ['model'], 'classes': ['required']}),
                    ('Advanced', {
                        'fields': ['targets', 'weight', 'delay', 'V_m', 'E_L', 'C_m', 't_ref', 'V_th', 'V_reset', 'E_ex', 'E_in', 'g_L', 'tau_syn_ex', 'tau_syn_in', 'I_e'], 
                        'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class ParrotForm(NeuronForm):
  
     class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay'], 'classes': ['required']}),
                    ('Advanced', {
                        'fields': [], 
                        'classes': ['advanced']}))
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
    
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    targets = forms.CharField(max_length=1000, help_text="Enter neuron id(s), e.g. '1,2,3' or '1-4'")
    weight = forms.CharField(max_length=1000, initial=1.0, label='Weight (pA)', help_text="Enter either positive or negative values.")
    delay = forms.CharField(max_length=1000, initial=1.0, label='Delay (ms)', help_text="Enter positive values < 10ms.")
    #synapse_type = forms.ChoiceField(choices=(('static_synapse', 'static synapse'),('tsodyks_synapse', 'tsodyks synapse')), help_text='')

    def as_div(self):
        return self._html_output(u'<div class="field-wrapper" title="%(help_text)s">%(label)s %(errors)s %(field)s</div>', u'%s', '</div>', u'%s', False)

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
    offset = forms.FloatField(required=False, label='Constant amplitude offset (pA)', help_text='')
    phase = forms.FloatField(required=False, label='Phase of sine current (0-360 deg)', help_text='Enter only values between 0 and 360.')
    frequency = forms.FloatField(required=False, initial=0., label='Frequency (Hz)', help_text='Enter only positive values.')

    def clean_amplitude(self):
        amplitude = self.cleaned_data.get('amplitude')
        if amplitude:
            try:
                # amplitude shouldn't be negative or zero.
                assert float(amplitude) > 0
            
            except:
                raise forms.ValidationError('Enter only values > 0.')
            
        return amplitude
        
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

    def clean_frequency(self):
        frequency = self.cleaned_data.get('frequency')
        if frequency:
            try:
                # frequency shouldn't be negative.
                assert float(frequency) >= 0
            
            except:
                raise forms.ValidationError('Enter only positive values.')
            
        return frequency

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay'], 'classes': ['required']}),
                    ('Advanced', {'fields': ['amplitude', 'frequency', 'offset', 'phase'], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class DCGeneratorForm(DeviceForm):
    amplitude = forms.FloatField(label='Amplitude of current (pA)', help_text='')

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay', 'amplitude'], 'classes': ['required']}),
                    ('Advanced', {'fields': [], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}

class NoiseGeneratorForm(DeviceForm):
    mean = forms.FloatField(required=False, label='Mean value of the noise current (pA)', help_text='')
    std = forms.FloatField(required=False, label='Standard deviation of noise current (pA)', help_text='Enter only positive values.')
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
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay'], 'classes': ['required']}),
                    ('Advanced', {'fields': ['mean', 'std', 'dt', 'start', 'stop'], 'classes': ['advanced']}))
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
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay', 'rate'], 'classes': ['required']}),
                    ('Advanced', {'fields': ['start', 'stop'], 'classes': ['advanced']}))
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
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay'], 'classes': ['required']}),
                    ('Advanced', {'fields': ['dc', 'ac', 'freq', 'phi'], 'classes': ['advanced']}))
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
        fieldsets = (('main', {'fields': ['model', 'targets', 'weight', 'delay', 'spike_times'], 'classes': ['required']}),
                    ('Advanced', {'fields': ['start', 'stop', 'step'], 'classes': ['advanced']}))
        row_attrs = {'model': {'is_hidden': True}}


""" 
General Forms
"""

class SourceForm(BetterForm):
    def __init__(self, network_obj=None, *args, **kwargs):
        self.instance = network_obj
        if args:
            self.neuron_ids = json.decode(str(args[0]['neuron_ids']))
        super(SourceForm, self).__init__(*args, **kwargs)
        
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    targets = forms.CharField(max_length=1000, help_text="Enter neuron id(s), e.g. '1,2,3' or '1-4'")


    def as_div(self):
        return self._html_output(u'<div class="field-wrapper" title="%(help_text)s">%(label)s %(errors)s %(field)s</div>', u'%s', '</div>', u'%s', False)

    def clean_targets(self):
        targets = self.cleaned_data.get('targets').replace(' ','')
        try:
            extended_list = values_extend(targets, unique=True)
        except:
            raise forms.ValidationError("Enter neuron id(s), e.g. '1,2,3' or '1-4'")
        
        # check if all targets are neurons
        neuron_ids = self.instance.neuron_ids()
        parrot_ids = self.instance.neuron_ids(label='parrot_neuron')
        
        for target in extended_list:
            if not (target in neuron_ids or target in self.neuron_ids):
                raise forms.ValidationError("Targets should be neurons.")
            if target in parrot_ids:
                raise forms.ValidationError("Some of the targets are not recordable.")
            
        return targets

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'targets'], 'classes': ['required']}),
                    ('Advanced', {'fields': [], 'classes': ['advanced']}))

class TargetForm(BetterForm):
    def __init__(self, network_obj=None, *args, **kwargs):
        self.instance = network_obj
        if args:
            self.neuron_ids = json.decode(str(args[0]['neuron_ids']))
        super(TargetForm, self).__init__(*args, **kwargs)
        
    model = forms.CharField(max_length=32, widget=forms.HiddenInput())
    sources = forms.CharField(max_length=1000, help_text="Enter neuron id(s), e.g. '1,2,3' or '1-4'")

    def as_div(self):
        return self._html_output(u'<div class="field-wrapper" title="%(help_text)s">%(label)s %(errors)s %(field)s</div>', u'%s', '</div>', u'%s', False)

    def clean_sources(self):
        sources = self.cleaned_data.get('sources').replace(' ','')
        try:
            extended_list = values_extend(sources, unique=True)
        except:
            raise forms.ValidationError("Enter neuron id(s), e.g. '1,2,3' or '1-4'")
        
        # check if all sources are neurons
        neuron_ids = self.instance.neuron_ids()
        parrot_ids = self.instance.neuron_ids(label='parrot_neuron')

        for source in extended_list:
            if not (source in neuron_ids or source in self.neuron_ids):
                raise forms.ValidationError("Sources should be neurons.")
            if source in parrot_ids:
                raise forms.ValidationError("Some of the sources are not recordable.")

        return sources

    class Meta:
        fieldsets = (('main', {'fields': ['model', 'sources'], 'classes': ['required']}),
                    ('Advanced', {'fields': [], 'classes': ['advanced']}))
