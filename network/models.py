# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
import numpy as np

import lib.json as json

from network.network_settings import ALL_PARAMS_ORDER

SPIC_CHOICES = (('0','Sandbox'),
                ('1','SPIC1'),
                ('2','SPIC2'),
                ('3','SPIC3'),
                ('4','SPIC4'))

class SPIC(models.Model):
    group = models.CharField(max_length=2, null=True, choices=SPIC_CHOICES)
    local_id = models.IntegerField(null=True)

    title = models.CharField(max_length=32, default='')
    description = models.TextField(blank=True)
    tooltip_json = models.TextField(blank=True)

    def __unicode__(self):
        return self.title

    def tooltip(self):
        if self.tooltip_json:
            return json.decode(str(self.tooltip_json))
        return {}


class Network(models.Model):
    user_id = models.IntegerField(null=True)
    SPIC = models.ForeignKey(SPIC, blank=True, null=True)
    local_id = models.IntegerField(null=True)

    label = models.CharField(max_length=32, blank=True, null=True)
    date_simulated = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True)

    duration = models.FloatField(null=True, default=1000.0)
    status_json = models.TextField(blank=True, verbose_name='Root status')
    devices_json = models.TextField(blank=True, verbose_name='Devices')

    nodes_json = models.TextField(blank=True, verbose_name='Nodes')
    links_json = models.TextField(blank=True, verbose_name='Links')

    has_voltmeter = models.BooleanField()
    has_spike_detector = models.BooleanField()
    voltmeter_json = models.TextField(blank=True, verbose_name='Voltmeter')
    spike_detector_json = models.TextField(blank=True, verbose_name='Spike Detector')

    favorite = models.BooleanField()
    deleted = models.BooleanField()

    class Meta:
        ordering = ('user_id', 'SPIC', 'local_id')

    def __unicode__(self):
        try:
            return '%s_%s_%s' %(self.user_id, self.SPIC, self.local_id)
        except:
            return '%s' %self.pk

    def copy(self):
        new_kwargs = dict([(fld.name, getattr(self, fld.name)) for fld in self._meta.fields if fld.name != 'id']);
        new_kwargs['deleted'] = False
        new_kwargs['favorite'] = False
        new_kwargs['label'] = ''
        new_kwargs['comment'] = ''
        return self.__class__.objects.create(**new_kwargs)

    def user(self):
        """
        Get user object from the django model 'auth' by user_id.
        CAUTION: the model 'User' is stored in other database.
        """
        if self.user_id == 0:
            return 'architect'
        else:
            return User.objects.get(pk=self.user_id)

    def root_status(self):
        """ Returns status data from the field status_json."""
        if self.status_json:
            return json.decode(str(self.status_json))
        return {}

    def nodes(self, term='visible', meta=False, key=None):
        if len(self.nodes_json) == 0: return []

        nodes = json.decode(self.nodes_json)

        # Get visible, hidden or all nodes
        if term == 'visible':
            nodes = filter(lambda node: (node['meta']['visible'] == 1), nodes)
        elif term == 'hidden':
            nodes = filter(lambda node: (node['meta']['visible'] == 0), nodes)

        # Meta data should not be visible for users
        if meta is False:
            for index in range(len(nodes)):
                del nodes[index]['meta']

        # Recounting ID
        for index in range(len(nodes)):
            nodes[index]['id'] = index+1

        # If key, get a list of its values
        if key:
            nodes = [node[key] for node in nodes if key in node]

        return nodes

    def nodes_csv(self):
        if len(self.nodes_json) == 0: return ""

        nodes = self.nodes()

        lst = []
        if nodes:
            for node in nodes:
                if node['type'] == 'neuron' and  self.SPIC.group == '1':
                    continue

                model = node['status']['model']
                if model in ALL_PARAMS_ORDER:
                    params_order = ALL_PARAMS_ORDER[model]
                    statusList = []
                    for key in params_order:
                        if key == 'id':
                            statusList.append(str(node.get(key)))
                        elif key in node['status']:
                            if node['status'][key]:
                                statusList.append(str(node['status'].get(key)))

                lst.append("; ".join(statusList))
        return "\r\n".join(lst)

    def neuron_ids(self):
        """
        Get a list of neuron ID for connectivity matrix and
        validation check of targets/sources.
        """
        nodes = [node for node in self.nodes() if node['type'] == 'neuron']
        if nodes:
            return [int(node['id']) for node in nodes]
        return []

    def links(self, term='visible', key=None, out='uid'):
        if len(self.links_json) == 0: return []

        links = json.decode(self.links_json)

        # Get nodes
        nodes = self.nodes(term)
        nodes_uid = [node['uid'] for node in nodes]

        # Get visible, hidden or all links
        if term == 'visible' or term == 'hidden':
            if term == 'visible':
                links = filter(lambda link: (link['source'] in nodes_uid and link['target'] in nodes_uid), links)
            if term == 'hidden':
                links = filter(lambda link: (link['source'] in nodes_uid or link['target'] in nodes_uid), links)

        # Output of source and target values
        if out == 'object':
            for index in range(len(links)):
                links[index]['source'] = nodes[nodes_uid.index(links[index]['source'])]
                links[index]['target'] = nodes[nodes_uid.index(links[index]['target'])]
        elif out != 'uid':
            for index in range(len(links)):
                if out in nodes[nodes_uid.index(links[index]['source'])]:
                    links[index]['source'] = nodes[nodes_uid.index(links[index]['source'])][out]
                if out in nodes[nodes_uid.index(links[index]['target'])]:
                    links[index]['target'] = nodes[nodes_uid.index(links[index]['target'])][out]

        # If key, get a list of its values
        if key:
            links = [link[key] for link in links if key in link]

        return links

    def update(self, nodes, links=None):

        # Add meta to visible nodes
        for index in range(len(nodes)):
            nodes[index]['meta'] = {'visible': 1}

        # Add hidden nodes
        nodes = sorted(nodes, key=lambda node: node['id'])
        nodes_hidden = self.nodes('hidden', meta=True)
        nodes += nodes_hidden

        # Recounting ID
        for index in range(len(nodes)):
            nodes[index]['id'] = index+1

        self.nodes_json = json.encode(nodes)

        if links:
            # Add hidden links
            links_hidden = self.links('hidden')
            links += links_hidden

            # Filter links
            nodes_uid = [node['uid'] for node in nodes]
            links = filter(lambda link: (link['source'] in nodes_uid and link['target'] in nodes_uid), links)

            for idx, val in enumerate(links):
                links[idx]['weight'] = float(val['weight'])
                links[idx]['delay'] = float(val['delay'])

            self.links_json = json.encode(links)

    def is_recorded(self):
        """ Check if the network is recorded. """
        return self.has_voltmeter or self.has_spike_detector

    def spike_detector_data(self, return_index=False):
        """ Decode spike detector data from json. """

        connect_to = [link['source']['id'] for link in self.links(out='object') if link['target']['status']['model'] == 'spike_detector']
        meta = {'neurons': [], 'simTime': self.duration, 'connect_to': connect_to}

        if self.has_spike_detector:
            data = json.decode(str(self.spike_detector_json))
            assert len(data['senders']) == len(data['times'])

            meta['neurons'] = data['meta']['neurons']
            data['meta'] = meta

            if return_index:
                senders = np.array(data['senders'])
                for idx, val in enumerate(meta['neurons']):
                    senders[senders==val['id']] = idx
                    data['meta']['neurons'][idx]['idx'] = idx
                data['senders'] = senders.tolist()
            return data

        return {'meta': meta}

    def spike_detector_data_index(self):
        return self.spike_detector_data(return_index=True)

    def voltmeter_data(self, sender=None):
        """ Decode voltmeter data from json. """

        connect_to = [link['target']['id'] for link in self.links(out='object') if link['source']['status']['model'] == 'voltmeter']
        meta = {'neurons': [], 'connect_to': connect_to}

        if self.has_voltmeter:
            def prep_to_vis(values):
                return {'values': values.tolist(), 'values_reduced': values[::5].tolist()}

            if len(self.voltmeter_json) > 0:
                vm_E = json.decode(str(self.voltmeter_json))
            else:
                vm_E = {'meta':{'neurons': []}, 'V_m': ''}
            meta['neurons'] = vm_E['meta']['neurons']

            V_m = vm_E['V_m']
            if len(V_m) > 0:
                V_m = np.reshape(np.array(V_m), [-1, len(meta['neurons'])]).T
                meta['Vm_max'] = np.max(V_m)
                meta['Vm_min'] = np.min(V_m)

            times = np.arange(1., self.duration, 1.)

            data = {'V_m': map(prep_to_vis, V_m), 'times':times.tolist(), 'times_reduced':times[::5].tolist()}
            data['meta'] = meta
            return data

        return {'meta': meta}

