# coding: utf-8

from django.conf.urls.defaults import *


urlpatterns = patterns('forum.views',
    url(r'^$', 'forum_list', name='forum'),
    url(r'^(?P<forum_id>\d+)/$', 'topic_list', name='forum'),
    url(r'^(?P<forum_id>\d+)/add/$', 'topic_add', name='topic_add'),
    url(r'^(?P<forum_id>\d+)/mark_read/$', 'forum_mark_read', name='forum_mark_read'),
    url(r'^forum/(?P<forum_id>\d+)/subscribe/$', 'subscribe_forum', name='subscribe_forum'),
    
    url(r'^topic/(?P<topic_id>\d+)/$', 'post_list', name='topic'),
    url(r'^topic/(?P<topic_id>\d+)/edit/$', 'topic_edit', name='topic_edit'),
    url(r'^topic/(?P<topic_id>\d+)/move/$', 'topic_move', name='topic_move'),
    url(r'^topic/(?P<topic_id>\d+)/post_move/$', 'post_move', name='post_move'),
    url(r'^topic/(?P<topic_id>\d+)/split/$', 'topic_split', name='topic_split'),
    url(r'^topic/(?P<topic_id>\d+)/stick/$', 'topic_stick', name='topic_stick'),
    url(r'^topic/(?P<topic_id>\d+)/close/$', 'topic_close', name='topic_close'),
    url(r'^topic/(?P<topic_id>\d+)/delete/$', 'topic_delete', name='topic_delete'),
    url(r'^topic/(?P<topic_id>\d+)/unread/$', 'unread_post_redirect', name='unread_post_redirect'),
    url(r'^topic/(?P<topic_id>\d+)/mark_read/$', 'topic_mark_read', name='topic_mark_read'),
    url(r'^topic/(?P<topic_id>\d+)/subscribe/$', 'subscribe_topic', name='subscribe_topic'),
    
    url(r'^post/(?P<post_id>\d+)/$', 'post_redirect', name='post_permalink'),
    url(r'^post/(?P<post_id>\d+)/edit/$', 'post_edit', name='post_edit'),
    url(r'^post/(?P<post_id>\d+)/delete/$', 'post_delete', name='post_delete'),
    url(r'^post/preview/', 'post_preview', name='post_preview'),
    
    url(r'^poll/vote/(?P<choice_id>\d+)/', 'poll_vote', name='poll_vote'),
)
