from django.conf.urls.defaults import url

import forum.feeds as forum_feeds
import news.feeds as news_feeds


urlpatterns = [
    # Forum feeds
    url(r'^topics/$', forum_feeds.TopicsFeed(), name='topics_feed'),
    url(r'^posts/$', forum_feeds.PostsFeed(), name='posts_feed'),
    url(r'^forum_topics/(?P<forum_id>\d+)/$', forum_feeds.ForumTopicsFeed(), name='forum_topics_feed'),
    url(r'^forum_posts/(?P<forum_id>\d+)/$', forum_feeds.ForumPostsFeed(), name='forum_posts_feed'),
    url(r'^topic_posts/(?P<topic_id>\d+)/$', forum_feeds.TopicPostsFeed(), name='topic_posts_feed'),

    # News feeds
    url(r'^news/$', news_feeds.NewsFeed(), name='news_feed'),
]
