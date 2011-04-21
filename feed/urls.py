# coding: utf-8

from django.conf.urls.defaults import *

from forum.feeds import *
from news.feeds import *


urlpatterns = patterns('',
    # Forum feeds
    url(r'^topics/$', TopicsFeed(), name='topics_feed'),
    url(r'^posts/$', PostsFeed(), name='posts_feed'),
    url(r'^forum_topics/(?P<forum_id>\d+)/$', ForumTopicsFeed(), name='forum_topics_feed'),
    url(r'^forum_posts/(?P<forum_id>\d+)/$', ForumPostsFeed(), name='forum_posts_feed'),
    url(r'^topic_posts/(?P<topic_id>\d+)/$', TopicPostsFeed(), name='topic_posts_feed'),
    
    # News feeds
    url(r'^news/$', NewsFeed(), name='news_feed'),
)
