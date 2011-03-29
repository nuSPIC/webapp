# coding: utf-8

from django.conf.urls.defaults import *


urlpatterns = patterns('news.views',
    url(r'^$', 'mainpage', name='mainpage'),
    url(r'^news/(?P<news_id>\d+)/$', 'single', name='news_single'),
    url(r'^news/archive/$', 'archive', name='news_archive'),
)
