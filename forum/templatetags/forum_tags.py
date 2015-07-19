# -*- coding: utf-8 -*-
# coding: utf-8

from django.conf import settings
from django.template import Library
from django.template.defaultfilters import stringfilter


register = Library()

@register.inclusion_tag('templatetags/topic_pagination.html')
def topic_pagination(topic):
    """
    Shows small topic pages navigation at topic list page
    """
    
    pages_count = 1 + (topic.posts_count - 1) / settings.TOPICS_PER_PAGE
    if pages_count == 1:
        pages_range = []
    else:
        left_range = range(1, pages_count+1)[:settings.TOPIC_PAGINATION_LEFT_TAIL]
        right_range = range(1, pages_count+1)[-settings.TOPIC_PAGINATION_RIGHT_TAIL:]
        pages_range = list(set(left_range + right_range))
        
        if (right_range[0] - left_range[-1]) > 1:
            pages_range.insert(pages_range.index(left_range[-1])+1, None)
    
    return {
        'topic': topic,
        'pages_range': pages_range,
    }

@register.inclusion_tag('templatetags/topic_actions.html')
def topic_actions(topic, perms, user):
    """
    Shows available topic actions for `user` with permissions `perms`
    """
    
    can_change = perms.can_change_topic(user, topic)
    can_move_topic = perms.can_move_topic(user, topic)
    can_move_post = perms.can_move_post(user, topic)
    can_split = perms.can_split_topic(user, topic)
    can_stick = perms.can_stick_topic(user, topic)
    can_close = perms.can_close_topic(user, topic)
    can_delete = perms.can_delete_topic(user, topic)
    
    return {
        'topic': topic,
        'can_change': can_change,
        'can_move_topic': can_move_topic,
        'can_move_post': can_move_post,
        'can_split': can_split,
        'can_stick': can_stick,
        'can_close': can_close,
        'can_delete': can_delete,
    }

@register.inclusion_tag('templatetags/post_actions.html')
def post_actions(post, perms, user):
    """
    Shows available post actions for `user` with permissions `perms`
    """
    
    if post.topic.first_post == post:
        # If it's first post of the topic check user topic edit permission
        can_change = perms.can_change_topic(user, post.topic)
        can_delete = perms.can_delete_topic(user, post.topic)
    else:
        # otherwise check user post edit permission
        can_change = perms.can_change_post(user, post)
        can_delete = perms.can_delete_post(user, post)
    
    return {
        'post': post,
        'user': user,
        'can_change': can_change,
        'can_delete': can_delete,
    }

@register.inclusion_tag('templatetags/post_editor.html', takes_context=True)
def post_editor(context, post_form):
    """
    Shows post edit form
    """
    
    return {
        'STATIC_URL': context['STATIC_URL'],
        'post_form': post_form,
    }
