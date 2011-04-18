# coding: utf-8

from django.db.models import Max, Count
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.utils import simplejson
from django.utils.timesince import timesince

from accounts.models import UserProfile
from forum.forms import *
from forum.inform import inform_new_topic, inform_new_post
from forum.models import Forum, Group, Post, Pool, PoolChoice, PoolVote, Topic
from forum.helpers import get_group_perms_or_404, is_subscribed, mark_read, mark_unread_forums, mark_unread_topics, do_subscribe
from lib.decorators import render_to
from lib.helpers import paginate

from bbmarkup import bbcode
from datetime import datetime


@render_to('forum/forum_list.html')
def forum_list(request):
    """
    Shows forum list user have permission to view
    """
    
    group = Group.group_for_user(request.user)
    visible_forums_ids = list(group.permission_set.values_list('forum_id', flat=True))
    forum_list = Forum.objects.filter(id__in=visible_forums_ids).order_by('priority').\
                               select_related('last_post', 'last_post__topic', 'last_post__profile', 'last_post__topic__last_post')
    mark_unread_forums(request.user, forum_list)
    
    # Popular topics
    visible_forums_ids = list(group.permission_set.values_list('forum_id', flat=True))
    popular_topics = Topic.objects.filter(post__date__gte=datetime.today()-settings.POPULAR_TOPICS_PERIOD, forum__id__in=visible_forums_ids, post__is_removed=False).\
                                   annotate(count=Count('post')).\
                                   order_by('-count')[:settings.POPULAR_TOPICS_COUNT]
    
    # New topics
    visible_forums_ids = list(group.permission_set.values_list('forum_id', flat=True))
    new_topics = Topic.objects.get_visible_topics().filter(forum__id__in=visible_forums_ids).order_by('-id')[:settings.NEW_TOPICS_COUNT]
    
    # Forum statistics
    total_posts_count = sum([forum.posts_count for forum in forum_list])
    total_topics_count = sum([forum.topics_count for forum in forum_list])
    total_users_count = UserProfile.objects.filter(user__is_active=True).count()
    novice_profile = User.objects.filter(is_active=True).latest('date_joined').get_profile()
    
    return {
        'forum_list': forum_list,
        
        'popular_topics': popular_topics,
        'new_topics': new_topics,
        
        'total_posts_count': total_posts_count,
        'total_topics_count': total_topics_count,
        'total_users_count': total_users_count,
        'novice_profile': novice_profile,
    }

@render_to('forum/topic_list.html')
def topic_list(request, forum_id):
    """
    Shows topic list in specified forum
    """
    
    forum = get_object_or_404(Forum, id=forum_id)
    group, perms = get_group_perms_or_404(request.user, forum)
    
    subscribed = is_subscribed(request.user, forum)
    
    topics = forum.topics.order_by('-is_sticked', '-last_post__date').\
                   select_related('last_post', 'last_post__profile', 'last_post__profile__user',
                                  'first_post', 'first_post__profile', 'first_post__profile__user')
    topic_list = paginate(request, topics, settings.TOPICS_PER_PAGE)
    mark_unread_topics(request.user, topic_list.object_list)
    
    return {
        'forum': forum,
        'subscribed': subscribed,
        'forum_perms': perms,
        'topic_list': topic_list,
    }

@login_required
def forum_mark_read(request, forum_id):
    """
    Mark all topics in specified forum as read and
    redirect to forum main page
    """
    
    forum = get_object_or_404(Forum, id=forum_id)
    get_group_perms_or_404(request.user, forum)
    
    profile = request.user.get_profile()
    readtracking = profile.readtracking
    
    for topic in forum.topics.only('id', 'last_post').select_related('last_post'):
        readtracking.last_read[topic.id] = topic.last_post.id
    readtracking.save()
    
    return HttpResponseRedirect(reverse('forum'))

@render_to('forum/topic_add.html')
@login_required
def topic_add(request, forum_id):
    """
    Adds new topic
    """
    
    forum = get_object_or_404(Forum, id=forum_id)
    group, perms = get_group_perms_or_404(request.user, forum)
    
    if perms.can_add_topic():
        PoolFormset = inlineformset_factory(Topic, Pool, fk_name='topic', form=PoolForm, max_num=10, extra=10)
        
        if request.method == 'POST':
            topic_form = TopicForm(request.POST, prefix='topic_form')
            post_form = PostForm(request.POST, prefix='post_form')
            pool_formset = PoolFormset(request.POST)
            
            if topic_form.is_valid() and post_form.is_valid() and pool_formset.is_valid():
                profile = request.user.get_profile()
                ip_address = request.META.get('REMOTE_ADDR', None)
                
                topic = topic_form.save(commit=False)
                topic.forum = forum
                topic.save()
                
                post = post_form.save(commit=False)
                post.topic = topic
                post.profile = profile
                post.ip_address = ip_address
                post.save()
                
                topic.first_post = post
                topic.save()
                
                # Save pool
                pool_formset.instance = topic
                for form in pool_formset.forms:
                    if hasattr(form, 'cleaned_data') and form.cleaned_data:
                        form.cleaned_data['topic'] = topic
                pool_formset.save()
                
                # Save pool choices
                for form in pool_formset.forms:
                    form.save_choices()
                
                # Inform subscribed users about new topic
                inform_new_topic(topic)
                
                # Auto subscribe user to his topic
                do_subscribe(profile, topic)
                
                return HttpResponseRedirect(topic.get_absolute_url())
        else:
            topic_form = TopicForm(prefix='topic_form')
            post_form = PostForm(prefix='post_form')
            pool_formset = PoolFormset()
    else:
        raise Http404
    
    return {
        'forum': forum,
        'topic_form': topic_form,
        'post_form': post_form,
        'pool_formset': pool_formset,
    }

@render_to('forum/topic_edit.html')
@login_required
def topic_edit(request, topic_id):
    """
    Edit topic and first post
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    post = topic.first_post
    forum = topic.forum
    
    group, perms = get_group_perms_or_404(request.user, forum)
    
    if perms.can_change_topic(request.user, topic):
        PoolFormset = inlineformset_factory(Topic, Pool, fk_name='topic', form=PoolForm, max_num=10, extra=10)
        
        if request.method == 'POST':
            topic_form = TopicForm(request.POST, instance=topic, prefix='topic_form')
            post_form = PostForm(request.POST, instance=post, prefix='post_form')
            pool_formset = PoolFormset(request.POST, instance=topic)
            
            if topic_form.is_valid() and post_form.is_valid() and pool_formset.is_valid():
                topic = topic_form.save()
                post = post_form.save()
                pool_formset.save()
                
                # Save pool choices
                for form in pool_formset.forms:
                    if form in pool_formset.deleted_forms:
                        continue
                    if form.instance.total_votes == 0:
                        form.save_choices()
                
                return HttpResponseRedirect(post.get_absolute_url())
        else:
            topic_form = TopicForm(instance=topic, prefix='topic_form')
            post_form = PostForm(instance=post, prefix='post_form')
            pool_formset = PoolFormset(instance=topic)
    else:
        return HttpResponseRedirect(topic.get_absolute_url())
    
    return {
        'forum': forum,
        'topic': topic,
        'post': post,
        'topic_form': topic_form,
        'post_form': post_form,
        'pool_formset': pool_formset,
    }

@render_to('forum/topic_move.html')
@login_required
def topic_move(request, topic_id):
    """
    Move topic to another forum
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    forum = topic.forum
    
    group, perms = get_group_perms_or_404(request.user, forum)
    
    if perms.can_move_topic(request.user, topic):
        if request.method == 'POST':
            topic_form = TopicMoveForm(request.POST, instance=topic)
            
            if topic_form.is_valid():
                topic_form.save()
                
                forum.update_topics_count()
                forum.update_posts_count()
                forum.update_last_post()
                forum.save()
                
                return HttpResponseRedirect(topic.get_absolute_url())
        else:
            topic_form = TopicMoveForm(instance=topic)
    else:
        return HttpResponseRedirect(topic.get_absolute_url())
    
    return {
        'forum': forum,
        'topic': topic,
        'topic_form': topic_form,
    }

@render_to('forum/post_move.html')
@login_required
def post_move(request, topic_id):
    """
    Move posts to another topic
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    forum = topic.forum
    
    group, perms = get_group_perms_or_404(request.user, forum)
    
    if perms.can_move_post(request.user, topic):
        if request.method == 'POST':
            topic_form = PostMoveForm(request.POST, user=request.user, topic_src=topic)
            
            if topic_form.is_valid():
                other_topic = topic_form.save()
                return HttpResponseRedirect(other_topic.get_absolute_url())
        else:
            topic_form = PostMoveForm(user=request.user, topic_src=topic)
    else:
        return HttpResponseRedirect(topic.get_absolute_url())
    
    return {
        'forum': forum,
        'topic': topic,
        'topic_form': topic_form,
    }

@render_to('forum/topic_split.html')
@login_required
def topic_split(request, topic_id):
    """
    Split topic
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    forum = topic.forum
    
    group, perms = get_group_perms_or_404(request.user, forum)
    
    if perms.can_split_topic(request.user, topic):
        if request.method == 'POST':
            topic_form = TopicSplitForm(request.POST, topic=topic)
            
            if topic_form.is_valid():
                new_topic = topic_form.save()
                return HttpResponseRedirect(new_topic.get_absolute_url())
        else:
            topic_form = TopicSplitForm(topic=topic)
    else:
        return HttpResponseRedirect(topic.get_absolute_url())
    
    return {
        'forum': forum,
        'topic': topic,
        'topic_form': topic_form,
    }

@login_required
def topic_stick(request, topic_id):
    """
    Stick / unstick topic
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    group, perms = get_group_perms_or_404(request.user, topic.forum)
    
    if perms.can_stick_topic(request.user, topic):
        topic.is_sticked = not topic.is_sticked
        topic.save()
    
    return HttpResponseRedirect(topic.get_absolute_url())

@login_required
def topic_close(request, topic_id):
    """
    Close / open topic
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    group, perms = get_group_perms_or_404(request.user, topic.forum)
    
    if perms.can_close_topic(request.user, topic):
        topic.is_closed = not topic.is_closed
        topic.save()
    
    return HttpResponseRedirect(topic.get_absolute_url())

@login_required
def topic_delete(request, topic_id):
    """
    Delete topic and redirect to topic list page
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    group, perms = get_group_perms_or_404(request.user, topic.forum)
    
    if perms.can_delete_topic(request.user, topic):
        topic.remove()
    
    return HttpResponseRedirect(topic.forum.get_absolute_url())

@login_required
def topic_mark_read(request, topic_id):
    """
    Mark all posts in specified topic as read and
    redirect to topic list page
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    get_group_perms_or_404(request.user, topic.forum)
    
    profile = request.user.get_profile()
    readtracking = profile.readtracking
    readtracking.last_read[topic.id] = topic.last_post.id
    readtracking.save()
    
    return HttpResponseRedirect(topic.forum.get_absolute_url())

@login_required
def unread_post_redirect(request, topic_id):
    """
    Redirect to the first unread post in specified topic
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    
    # Get last read post id in topic
    profile = request.user.get_profile()
    readtracking = profile.readtracking
    last_read_post_id = readtracking.last_read.get(topic.id, 0)
    
    # Find first unread post and calculate topic page.
    # In the case if unread posts not found redirect user to first page of topic.
    new_posts = topic.posts.filter(id__gt=last_read_post_id).order_by('id')
    if new_posts:
        first_new_post = new_posts[0]
        posts_before = topic.posts.filter(date__lt=first_new_post.date).count()
        page = 1 + posts_before / settings.POSTS_PER_PAGE
        post_link = '?page=%s#post%s' % (page, first_new_post.id)
        
        return HttpResponseRedirect(topic.get_absolute_url() + post_link)
    else:
        return HttpResponseRedirect(topic.get_absolute_url())

@render_to('forum/post_list.html')
def post_list(request, topic_id):
    """
    Shows posts list in specified topic and process add new post 
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    forum = topic.forum
    group, perms = get_group_perms_or_404(request.user, forum)
    
    subscribed = is_subscribed(request.user, topic)
    
    if perms.can_add_post(topic):
        if request.method == 'POST':
            post_form = PostForm(request.POST, prefix='post_form')
            
            if post_form.is_valid():
                profile = request.user.get_profile()
                
                # Glue two consecutive posts from same user if time interval between them less than GLUE_MESSAGE_TIMEOUT
                delta = (datetime.today()-topic.last_post.date).seconds
                if (topic.last_post.profile == profile) and (delta < settings.GLUE_MESSAGE_TIMEOUT):
                    post = topic.last_post
                    glue_message = post.message + settings.GLUE_MESSAGE % (timesince(post.date), post_form.cleaned_data['message'])
                    data = {'message': glue_message}
                    
                    if PostForm(data).is_valid():
                        post.message = glue_message
                        post.save()
                        return HttpResponseRedirect(post.get_absolute_url())
                
                ip_address = request.META.get('REMOTE_ADDR', None)
                
                post = post_form.save(commit=False)
                post.topic = topic
                post.profile = profile
                post.ip_address = ip_address
                post.save()
                
                # Inform subscribed users about new post
                inform_new_post(post)
                
                return HttpResponseRedirect(post.get_absolute_url())
        else:
            post_form = PostForm(prefix='post_form')
    else:
        post_form = None
    
    posts = topic.posts.order_by('date').select_related('profile', 'profile__user', 'profile__group', 'topic', 'topic__first_post')
    post_list = paginate(request, posts, settings.POSTS_PER_PAGE)
    
    # Generate pool list for the first topic page
    if post_list.number == 1:
        pools = topic.pools.annotate(max_votes_count=Max('choices__votes_count'))
        pools_ids = list(pools.values_list('id', flat=True))
        
        # Select dictionary of user choices for topic pools
        if request.user.is_authenticated():
            profile = request.user.get_profile()
            pool_votes = dict(PoolVote.objects.filter(profile=profile, pool__in=pools_ids).values_list('pool', 'choice'))
        else:
            pool_votes = {}
        
        # For every pool in sequence set:
        #  - user_can_vote, ability user to vote in specified pool
        #  - user_vote, user vote for specified pool
        for pool in pools:
            pool.user_can_vote = not bool(pool.expired() or request.user.is_anonymous() or bool(pool.id in pool_votes.keys()))
            if pool.id in pool_votes.keys():
                pool.user_vote = pool_votes[pool.id]
    else:
        pools = []
    
    mark_read(request.user, post_list.object_list)
    
    return {
        'forum': forum,
        'topic': topic,
        'pools': pools,
        'subscribed': subscribed,
        'forum_perms': perms,
        'post_list': post_list,
        'post_form': post_form,
    }

@render_to('forum/post_edit.html')
@login_required
def post_edit(request, post_id):
    """
    Post edit
    """
    
    post = get_object_or_404(Post, id=post_id)
    topic = post.topic
    forum = topic.forum
    
    group, perms = get_group_perms_or_404(request.user, forum)
    
    if perms.can_change_post(request.user, post):
        if request.method == 'POST':
            post_form = PostForm(request.POST, instance=post, prefix='post_form')
            
            if post_form.is_valid():
                post = post_form.save()
                return HttpResponseRedirect(post.get_absolute_url())
        else:
            post_form = PostForm(instance=post, prefix='post_form')
    else:
        return HttpResponseRedirect(post.get_absolute_url())
    
    return {
        'forum': forum,
        'topic': topic,
        'post': post,
        'post_form': post_form,
    }

@login_required
def post_delete(request, post_id):
    """
    Delete post and redirect back to page
    """
    
    post = get_object_or_404(Post, id=post_id)
    group, perms = get_group_perms_or_404(request.user, post.topic.forum)
    
    if perms.can_delete_post(request.user, post):
        post.remove()
        
    # Redirect to post before deleted one
    prev_post = post.topic.posts.filter(date__lt=post.date).reverse()[0]
    
    return HttpResponseRedirect(prev_post.get_absolute_url())

def post_redirect(request, post_id):
    """
    Redirect to page with specified post
    """
    
    post = get_object_or_404(Post, id=post_id)
    
    posts_before = post.topic.posts.filter(date__lt=post.date).count()
    page = 1 + posts_before / settings.POSTS_PER_PAGE
    post_link = '?page=%s#post%s' % (page, post_id)
    
    return HttpResponseRedirect(post.topic.get_absolute_url() + post_link)

@login_required
def post_preview(request):
    """
    Post preview. Works only with AJAX requests.
    Get post form data with required `post_form` prefix.
    Return HTML compiled post.
    """
    
    if request.is_ajax():
        post_form = PostForm(request.POST, prefix='post_form')
        if post_form.is_valid():
            profile = request.user.get_profile()
            message_html = bbcode(post_form.cleaned_data['message'])
            response = render_to_string('forum/post_preview.html', {'profile': profile, 'message_html': message_html})
            return HttpResponse(response, mimetype='text/html')
    
    return HttpResponse()

@login_required
@never_cache
def pool_vote(request, choice_id):
    """
    Pool voting. Works only with AJAX requests.
    Returns JSON with poll vote results.
    """
    
    choice = get_object_or_404(PoolChoice, id=choice_id)
    
    if request.is_ajax():
        profile = request.user.get_profile()
        
        if choice.pool.expired():
            return HttpResponse()
        
        PoolVote.objects.get_or_create(profile=profile, pool=choice.pool, choice=choice)
        pool = Pool.objects.filter(id=choice.pool.id).annotate(max_votes_count=Max('choices__votes_count'))[0]
        pool.user_vote = choice.id
        pool.user_can_vote = False
        
        # Compile HTML pool results
        responseHTML = render_to_string('forum/pool_results.html', {'pool': pool})
        response = {
            'pool_id': pool.id,
            'responseHTML': responseHTML
        }
        return HttpResponse(simplejson.dumps(response), mimetype='application/json')
    else:
        return HttpResponseRedirect(choice.pool.topic.get_absolute_url())


# ======================
#   Subscription
# ======================

@login_required
@never_cache
def subscribe_forum(request, forum_id):
    """
    Subscribe specified forum for new topics notification
    """
    
    forum = get_object_or_404(Forum, id=forum_id)
    
    profile = request.user.get_profile()
    do_subscribe(profile, forum)
    
    return HttpResponseRedirect(forum.get_absolute_url())

@login_required
@never_cache
def subscribe_topic(request, topic_id):
    """
    Subscribe specified topic for new posts notification
    """
    
    topic = get_object_or_404(Topic, id=topic_id)
    
    profile = request.user.get_profile()
    do_subscribe(profile, topic)
    
    return HttpResponseRedirect(topic.get_absolute_url())
