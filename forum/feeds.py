# coding: utf-8

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.utils.safestring import mark_safe

from accounts.models import Group
from forum.models import Forum, Topic, Post
from forum.helpers import get_group_perms_or_404

__all__ = ('TopicsFeed', 'PostsFeed', 'ForumTopicsFeed', 'ForumPostsFeed', 'TopicPostsFeed',)


# Get current site and retrieve the site name
current_site = Site.objects.get_current()
site_name = current_site.name


class TopicsFeed(Feed):
    """
    New topics
    """
    
    title = u'%s > Discussions > New topics' % site_name
    description = u'New topics in %s discussion forum' % site_name
    
    def link(self):
        return reverse('forum')
    
    def items(self):
        """
        Returns new topics in forums, which anonymous users can access
        """
        
        group = Group.anonymous_group()
        visible_forums_ids = list(group.permission_set.values_list('forum_id', flat=True))
        topics = Topic.objects.get_visible_topics().\
                               filter(forum__id__in=visible_forums_ids).\
                               order_by('-id').\
                               select_related()[:settings.FORUM_FEED_ITEMS_COUNT]
        
        return topics
    
    def item_title(self, item):
        return escape(u'New topic by %s: %s' % (unicode(item.first_post.profile), unicode(item)))
    
    def item_description(self, item):
        return mark_safe(item.first_post.message_html)


class PostsFeed(Feed):
    """
    New posts
    """
    
    title = u'%s > Discussions > New posts' % site_name
    description = u'New posts in %s discussion forum' % site_name
    
    def link(self):
        return reverse('forum')
    
    def items(self):
        """
        Returns new posts in forums, which anonymous users can access
        """
        
        group = Group.anonymous_group()
        visible_forums_ids = list(group.permission_set.values_list('forum_id', flat=True))
        posts = Post.objects.get_visible_posts().\
                             filter(topic__forum__id__in=visible_forums_ids).\
                             order_by('-date').\
                             select_related()[:settings.FORUM_FEED_ITEMS_COUNT]
        
        return posts
    
    def item_title(self, item):
        return escape(u'%s wrote' % unicode(item.profile))
    
    def item_description(self, item):
        return mark_safe(item.message_html)


class ForumTopicsFeed(Feed):
    """
    New topics in specified forum
    """
    
    def title(self, forum):
        return u'%s > Discussions > %s > New topics' % (site_name, forum.name)
    
    def description(self, forum):
        return u'New topics in %s' % forum.name
    
    def link(self, forum):
        return forum.get_absolute_url()
    
    def get_object(self, request, forum_id):
        return get_object_or_404(Forum, id=forum_id)
    
    def items(self, forum):
        """
        Returns new topics in the specified forum, if anonymous users can access it
        """
        
        get_group_perms_or_404(AnonymousUser(), forum)
        topics = forum.topics.order_by('-id').select_related()[:settings.FORUM_FEED_ITEMS_COUNT]
        
        return topics
    
    def item_title(self, item):
        return escape(u'New topic by %s: %s' % (unicode(item.first_post.profile), unicode(item)))
    
    def item_description(self, item):
        return mark_safe(item.first_post.message_html)


class ForumPostsFeed(Feed):
    """
    New posts in specified forum
    """
    
    def title(self, forum):
        return u'%s > Discussions > %s > New posts' % (site_name, forum.name)
    
    def description(self, forum):
        return u'New posts in %s' % forum.name
    
    def link(self, forum):
        return forum.get_absolute_url()
    
    def get_object(self, request, forum_id):
        return get_object_or_404(Forum, id=forum_id)
    
    def items(self, forum):
        """
        Returns new posts in the specified forum, if anonymous users can access it
        """
        
        get_group_perms_or_404(AnonymousUser(), forum)
        posts = forum.posts.order_by('-date').select_related()[:settings.FORUM_FEED_ITEMS_COUNT]
        
        return posts
    
    def item_title(self, item):
        return escape(u'%s commented on %s' % (unicode(item.profile), unicode(item.topic)))
    
    def item_description(self, item):
        return mark_safe(item.message_html)


class TopicPostsFeed(Feed):
    """
    New posts in specified topic
    """
    
    def title(self, topic):
        return u'%s > Discussions > %s > %s > New posts' % (site_name, topic.forum.name, topic.name)
    
    def description(self, topic):
        return u'New posts in %s' % topic.name
    
    def link(self, topic):
        return topic.get_absolute_url()
    
    def get_object(self, request, topic_id):
        return get_object_or_404(Topic, id=topic_id)
    
    def items(self, topic):
        """
        Returns new posts in the specified topic, if anonymous user can access it
        """
        
        get_group_perms_or_404(AnonymousUser(), topic.forum)
        posts = topic.posts.order_by('-date').select_related()[:settings.FORUM_FEED_ITEMS_COUNT]
        
        return posts
    
    def item_title(self, item):
        return escape(u'%s wrote' % unicode(item.profile))
    
    def item_description(self, item):
        return mark_safe(item.message_html)
