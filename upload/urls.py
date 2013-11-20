from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('upload.views',
    url(r'^$', 'upload_file', name='upload_file'),
    )
