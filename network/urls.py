# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('network.views',
    url(r'^$', 'network_list', name='network_list'),
    url(r'^(?P<SPIC_id>\d+)/(?P<local_id>\d+)/$', 'network', name='network'),
    url(r'^(?P<SPIC_id>\d+)/(?P<local_id>\d+)/(?P<result_id>\d+)/$', 'network_simulated', name='network-simulated'),
    
    # These following requests work with AJAX.
    url(r'^ajax/(?P<network_id>\d+)/(?P<version_id>\d+)/simulate/$', 'simulate', name='simulate'),
    url(r'^ajax/(?P<network_id>\d+)/device_preview/$', 'device_preview', name='device_preview'),
    url(r'^ajax/(?P<network_id>\d+)/device_commit/$', 'device_commit', name='device_commit'),
    url(r'^ajax/(?P<network_id>\d+)/default_layout/$', 'default_layout', name='default_layout'),
    )
