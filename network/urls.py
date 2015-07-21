from django.conf.urls.defaults import url

import views

urlpatterns = [
    url(r'^$', views.network_list, name='network_list'),

    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/$', views.network_latest, name='network_latest'),
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/initial/$', views.network_initial, name='network_initial'),
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/history/$', views.network_history, name='network_history'),
    url(r'^(?P<SPIC_group>\d+)/(?P<SPIC_id>\d+)/(?P<local_id>\d+)/$', views.network, name='network'),

    # Following requests are responsing with AJAX.
    url(r'^ajax/task_abort/$', views.abort, name='task_abort'),
    url(r'^ajax/task_status/$', views.status, name='task_status'),

    url(r'^ajax/(?P<network_id>\d+)/comment/$', views.network_comment, name='network_comment'),
    url(r'^ajax/(?P<network_id>\d+)/dislike/$', views.network_dislike, name='network_dislike'),
    url(r'^ajax/(?P<network_id>\d+)/like/$', views.network_like, name='network_like'),
#    url(r'^ajax/(?P<network_id>\d+)/device_csv/$', 'device_csv', name='device_csv'),
#    url(r'^ajax/(?P<network_id>\d+)/device_preview/$', 'device_preview', name='device_preview'),
#    url(r'^ajax/(?P<network_id>\d+)/device_commit/$', 'device_commit', name='device_commit'),
    url(r'^ajax/(?P<network_id>\d+)/save_label/$', views.label_save, name='save_label'),
    url(r'^ajax/(?P<network_id>\d+)/save_layout/$', views.layout_save, name='save_layout'),
    url(r'^ajax/(?P<network_id>\d+)/default_layout/$', views.layout_default, name='default_layout'),
    url(r'^ajax/(?P<network_id>\d+)/simulate/$', views.simulate, name='simulate'),
    url(r'^ajax/(?P<network_id>\d+)/data/$', views.data, name='data'),
]
