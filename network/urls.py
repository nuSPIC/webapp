# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('network.views',
    url(r'^$', 'network_list', name='network_list'),

    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/$', 'network_latest', name='network_latest'),
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/initial/$', 'network_initial', name='network_initial'),
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/history/$', 'network_history', name='network_history'),
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/(?P<local_id>\d+)/$', 'network', name='network'),

    # Following requests are responsing with AJAX.
    url(r'^ajax/(?P<task_id>\d+)/abort/$', 'abort', name='abort'),
    url(r'^ajax/(?P<network_id>\d+)/simulate/$', 'simulate', name='simulate'),
    url(r'^ajax/(?P<network_id>\d+)/delete/$', 'network_delete', name='network_delete'),
    url(r'^ajax/(?P<network_id>\d+)/revert/$', 'network_revert', name='network_revert'),
    url(r'^ajax/(?P<network_id>\d+)/device_csv/$', 'device_csv', name='device_csv'),
    url(r'^ajax/(?P<network_id>\d+)/device_preview/$', 'device_preview', name='device_preview'),
    url(r'^ajax/(?P<network_id>\d+)/device_commit/$', 'device_commit', name='device_commit'),
    
    url(r'^ajax/(?P<network_id>\d+)/save_label/$', 'label_save', name='save_label'),
    url(r'^ajax/(?P<network_id>\d+)/save_layout/$', 'layout_save', name='save_layout'),
    url(r'^ajax/(?P<network_id>\d+)/default_layout/$', 'layout_default', name='default_layout'),
    
    url(r'^ajax/(?P<network_id>\d+)/data/$', 'data', name='data'),
    )
