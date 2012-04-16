# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('network.views',
    url(r'^$', 'network_list', name='network_list'),

    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/$', 'network_latest', name='network_latest'),
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/initial/$', 'network_initial', name='network_initial'),
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/split/$', 'network_split', name='network_split'),
    
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/(?P<local_id>\d+)/$', 'network', name='network'),
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/(?P<local_id>\d+)/mini/$', 'network_mini', name='network_mini'),
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/(?P<local_id>\d+)/layout/$', 'network_layout', name='network_layout'),
    
    # Following requests are responsing with AJAX.
    url(r'^ajax/(?P<task_id>\d+)/abort/$', 'abort', name='abort'),
    url(r'^ajax/(?P<network_id>\d+)/simulate/$', 'simulate', name='simulate'),
    url(r'^ajax/(?P<network_id>\d+)/device_csv/$', 'device_csv', name='device_csv'),
    url(r'^ajax/(?P<network_id>\d+)/device_preview/$', 'device_preview', name='device_preview'),
    url(r'^ajax/(?P<network_id>\d+)/device_commit/$', 'device_commit', name='device_commit'),
    
    url(r'^ajax/(?P<network_id>\d+)/save_label/$', 'label_save', name='save_label'),   
    url(r'^ajax/(?P<network_id>\d+)/save_layout/$', 'layout_save', name='save_layout'),
    url(r'^ajax/(?P<network_id>\d+)/default_layout/$', 'default_layout', name='default_layout'),
    
    url(r'^ajax/(?P<network_id>\d+)/data/$', 'data', name='data'),
    url(r'^ajax/(?P<network_id>\d+)/voltmeter/$', 'voltmeter', name='voltmeter'),
    url(r'^ajax/(?P<network_id>\d+)/voltmeter_thumbnail/$', 'voltmeter_thumbnail', name='voltmeter_thumbnail'),
    url(r'^ajax/(?P<network_id>\d+)/spike_detector/$', 'spike_detector', name='spike_detector'),
    )
