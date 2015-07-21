from django.conf.urls.defaults import url

import views

urlpatterns = [
    url(r'^$', views.mainpage, name='mainpage'),
    url(r'^news/(?P<news_id>\d+)/$', views.single, name='news_single'),
    url(r'^news/archive/$', views.archive, name='news_archive'),
]
