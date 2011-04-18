# coding: utf-8

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from forum.models import Forum, Permission, Topic, Subscription


def inform_new_topic(topic):
    """
    Inform users about new topic in subscribed forum
    """
    
    forum_type = ContentType.objects.get_for_model(Forum)
    subscriptions = Subscription.objects.filter(content_type=forum_type, object_id=topic.forum.id).select_related()
    topic_author = topic.first_post.profile
    
    current_site = Site.objects.get_current()
    site_name = current_site.name
    domain = current_site.domain
    
    context = {
        'site_name': site_name,
        'domain': domain,
        'topic': topic,
    }

    for subscription in subscriptions:
        profile = subscription.profile
        if topic_author != profile:
            # Check user access to subscribed forum
            try:
                profile.forum_group.permission_set.get(forum=topic.forum)
            except Permission.DoesNotExist:
                pass
            else:
                # Inform user by email about new post
                if profile.forum_email_notification:
                    subject = u'New topic in forum "%s"' % topic.forum.name
                    message = render_to_string('delivery/forum_topic_mail.txt', context)
                    profile.user.email_user(subject, message)

def inform_new_post(post):
    """
    Inform users about new post in subscribed topic
    """
    
    topic_type = ContentType.objects.get_for_model(Topic)
    subscriptions = Subscription.objects.filter(content_type=topic_type, object_id=post.topic.id).select_related()
    post_author = post.profile
    
    current_site = Site.objects.get_current()
    site_name = current_site.name
    domain = current_site.domain
    
    context = {
        'site_name': site_name,
        'domain': domain,
        'post': post,
    }
    
    for subscription in subscriptions:
        profile = subscription.profile
        if post_author != profile:
            # Check user access to subscribed forum
            try:
                profile.forum_group.permission_set.get(forum=post.topic.forum)
            except Permission.DoesNotExist:
                pass
            else:
                # Inform user by email about new post
                if profile.forum_email_notification:
                    subject = u'New post in topic "%s"' % post.topic.name
                    message = render_to_string('delivery/forum_post_mail.txt', context)
                    profile.user.email_user(subject, message)
