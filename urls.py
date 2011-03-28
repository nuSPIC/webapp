# coding: utf-8

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin


# Activating django admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)

# Serving static files in django development server mode
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
