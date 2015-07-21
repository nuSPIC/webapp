from django.conf.urls.defaults import url

import views

urlpatterns = [
    url(r'^$', views.forum_list, name='forum'),
    url(r'^(?P<forum_id>\d+)/$', views.topic_list, name='forum'),
    url(r'^(?P<forum_id>\d+)/add/$', views.topic_add, name='topic_add'),
    url(r'^(?P<forum_id>\d+)/mark_read/$', views.forum_mark_read, name='forum_mark_read'),
    url(r'^(?P<forum_id>\d+)/subscribe/$', views.subscribe_forum, name='subscribe_forum'),
    url(r'^subscriptions/$', views.forum_subscription, name='forum_subscription'),

    url(r'^topic/(?P<topic_id>\d+)/$', views.post_list, name='topic'),
    url(r'^topic/(?P<topic_id>\d+)/edit/$', views.topic_edit, name='topic_edit'),
    url(r'^topic/(?P<topic_id>\d+)/move/$', views.topic_move, name='topic_move'),
    url(r'^topic/(?P<topic_id>\d+)/post_move/$', views.post_move, name='post_move'),
    url(r'^topic/(?P<topic_id>\d+)/split/$', views.topic_split, name='topic_split'),
    url(r'^topic/(?P<topic_id>\d+)/stick/$', views.topic_stick, name='topic_stick'),
    url(r'^topic/(?P<topic_id>\d+)/close/$', views.topic_close, name='topic_close'),
    url(r'^topic/(?P<topic_id>\d+)/delete/$', views.topic_delete, name='topic_delete'),
    url(r'^topic/(?P<topic_id>\d+)/unread/$', views.unread_post_redirect, name='unread_post_redirect'),
    url(r'^topic/(?P<topic_id>\d+)/mark_read/$', views.topic_mark_read, name='topic_mark_read'),
    url(r'^topic/(?P<topic_id>\d+)/subscribe/$', views.subscribe_topic, name='subscribe_topic'),

    url(r'^post/$', views.post_list_all, name='post_list'),
    url(r'^post/(?P<post_id>\d+)/$', views.post_redirect, name='post_permalink'),
    url(r'^post/(?P<post_id>\d+)/edit/$', views.post_edit, name='post_edit'),
    url(r'^post/(?P<post_id>\d+)/delete/$', views.post_delete, name='post_delete'),
    url(r'^post/preview/', views.post_preview, name='post_preview'),

    url(r'^poll/vote/(?P<choice_id>\d+)/', views.poll_vote, name='poll_vote'),

    url(r'^search/', views.search, name='search'),
]
