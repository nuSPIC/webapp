from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from .models import Group, Subscription


def get_group_perms_or_404(user, forum):
    """
    Returns user's group and group permissions for the specific forum
    """

    group = Group.group_for_user(user)
    try:
        perms = group.permission_set.get(forum=forum)
    except ObjectDoesNotExist:
        raise Http404

    return group, perms

def mark_unread_forums(user, forums):
    """
    Returns the list of the forums with unread flag set to True
    for forums that have unread topics for specified user
    """

    if user.is_authenticated():
        profile = user.get_profile()
        last_read = profile.readtracking.last_read

        for forum in forums:
            if forum.last_post:
                last_post_topic_id = forum.last_post.topic.id
                last_read_post_id = last_read.get(last_post_topic_id, 0)

                # Quick check
                if forum.last_post.id > last_read_post_id:
                    setattr(forum, 'unread', True)
                else:
                    # Get last FORUM_UNREAD_DEPTH topics and check for unread posts
                    last_topics = forum.topics.order_by('-last_post__date').values('id', 'last_post_id')[:settings.FORUM_UNREAD_DEPTH]
                    for topic in last_topics:
                        last_read_post_id = last_read.get(topic['id'], 0)
                        if topic['last_post_id'] > last_read_post_id:
                            setattr(forum, 'unread', True)
                            break
                    else:
                        setattr(forum, 'unread', False)

def mark_unread_topics(user, topics):
    """
    Returns the list of the topics with unread flag set to True
    for topics that have unread posts for specified user
    """

    if user.is_authenticated():
        profile = user.get_profile()
        last_read = profile.readtracking.last_read

        for topic in topics:
            last_read_post_id = last_read.get(topic.id, 0)
            setattr(topic, 'unread', bool(topic.last_post.id > last_read_post_id))

def mark_read(user, posts):
    """
    Saves the id of the last post in the list of posts in user readtracking
    """

    if user.is_authenticated():
        profile = user.get_profile()
        readtracking = profile.readtracking

        last_post = list(posts.values())[-1]
        last_read_post_id = readtracking.last_read.get(last_post['topic_id'], 0)

        if last_post['id'] > last_read_post_id:
            readtracking.last_read[last_post['topic_id']] = last_post['id']
            readtracking.save()

def is_subscribed(user, object):
    """
    Returns whether the user is subscribed to an object or not
    """

    if user.is_authenticated():
        forum_type = ContentType.objects.get_for_model(object.__class__)
        try:
            Subscription.objects.get(profile=user.get_profile(), content_type=forum_type, object_id=object.id)
        except Subscription.DoesNotExist:
            return False
        else:
            return True
    else:
        return False

def do_subscribe(profile, object):
    """
    Subscribe the user to the object. Next function call unsubscribes the user.
    Returns created `Subscription` object or None.
    """

    object_type = ContentType.objects.get_for_model(object)
    obj, created = Subscription.objects.get_or_create(profile=profile, content_type=object_type, object_id=object.id)

    if not created:
        obj.delete()
