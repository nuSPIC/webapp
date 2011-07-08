from django.conf.urls.defaults import patterns, url
from django.views.generic import list_detail
from network.models import Network

network_info = {
    "queryset" : Network.objects.filter(user_id=0),
}

urlpatterns = patterns ('', 
    url(r'^$', list_detail.object_list, network_info, name='network_list'),
    )

urlpatterns += patterns('network.views',
    
    url(r'^(?P<SPIC_id>\d+)/(?P<local_network_id>\d+)/$', 'network', name='network'),
    
    # These following requests are in Ajax.
    url(r'^ajax/(?P<network_id>\d+)/(?P<version_id>\d+)/simulate/$', 'simulate', name='simulate'),
    url(r'^ajax/(?P<network_id>\d+)/device_preview/$', 'device_preview', name='device_preview'),
    url(r'^ajax/(?P<network_id>\d+)/device_commit/$', 'device_commit', name='device_commit'),
    )
