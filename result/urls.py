from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('result.views',
    url(r'^(?P<result_id>\d+)/comment/$', 'result_comment', name='result_comment'),
    url(r'^(?P<result_id>\d+)/data/$', 'data', name='data'),

    url(r'^(?P<result_id>\d+)/voltmeter/$', 'voltmeter', name='voltmeter'),
    url(r'^(?P<result_id>\d+)/voltmeter_thumbnail/$', 'voltmeter_thumbnail', name='voltmeter_thumbnail'),
    
    url(r'^(?P<result_id>\d+)/spike_detector/$', 'spike_detector', name='spike_detector'),
    url(r'^(?P<result_id>\d+)/spike_detector_thumbnail/$', 'spike_detector_thumbnail', name='spike_detector_thumbnail'),
    )