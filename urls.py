# -*- coding: utf-8 -*-
# coding: utf-8

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from djcelery import views as celery_views


# Activate Django admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('news.urls')),
    (r'^accounts/', include('accounts.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^feed/', include('feed.urls')),
    (r'^forum/', include('forum.urls')),
    (r'^network/', include('network.urls')),
    (r'^result/',  include('result.urls')),

    url(r'^status/(?P<task_id>[\w\d\-]+)/?$', celery_views.task_status, name="celery_task_status"),
)

# Serve static files in Django development server mode
#if settings.DEBUG:
urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
