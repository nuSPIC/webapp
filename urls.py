# coding: utf-8

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin


# Activate Django admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('news.urls')),
    (r'^accounts/', include('accounts.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^forum/', include('forum.urls')),
)

# Serve static files in Django development server mode
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
