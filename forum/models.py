# coding: utf-8

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models

from accounts.models import UserProfile, Group
from forum.fields import SerializedField
from lib.decorators import signals
from lib.helpers import load_content_objects

from bbmarkup import bbcode
from datetime import date


# ==========================
#   Forum models
# ==========================

class Forum(models.Model):
    name = models.CharField('Forum title', max_length=250)
    description = models.CharField('Forum description', max_length=250)
    priority = models.PositiveSmallIntegerField('Forum list priority', default=0, help_text='Smaller the value, higher the position')
    topics_count = models.PositiveIntegerField('Number of topics', default=0)
    posts_count = models.PositiveIntegerField('Number of posts', default=0)
    last_post = models.ForeignKey('Post', verbose_name='Last post', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Forum'
        verbose_name_plural = 'Forums'
        ordering = ['priority']
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('forum', (), {'forum_id': self.id})
    
    @property
    def topics(self):
        return Topic.objects.get_visible_topics().filter(forum=self)
    
    @property
    def posts(self):
        return Post.objects.get_visible_posts().filter(topic__forum=self)
    
    def update_topics_count(self):
        self.topics_count = self.topics.count()
    
    def update_posts_count(self):
        self.posts_count = self.posts.count()
    
    def update_last_post(self):
        try:
            self.last_post = self.posts.latest('date')
        except Post.DoesNotExist:
            self.last_post = None


class TopicManager(models.Manager):
    def get_visible_topics(self):
        return self.get_query_set().filter(is_removed=False)

class Topic(models.Model):
    forum = models.ForeignKey(Forum, verbose_name='Forum')
    name = models.CharField('Topic title', max_length=250)
    
    posts_count = models.PositiveIntegerField('Number of posts', default=0)
    first_post = models.ForeignKey('Post', verbose_name='First post', related_name='first_for_topic', null=True, blank=True)
    last_post = models.ForeignKey('Post', verbose_name='Last post', related_name='last_for_topic', null=True, blank=True)
    
    is_sticked = models.BooleanField('Is sticked', default=False)
    is_closed = models.BooleanField('Is closed', default=False)
    is_removed = models.BooleanField('Is removed', default=False)
    
    objects = TopicManager()
    
    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        ordering = ['-is_sticked', '-last_post__date']
        permissions = (
            ('move_topic', 'Can move topic to another forum'),
            ('split_topic', 'Can split topic'),
            ('stick_topic', 'Can stick topic'),
            ('close_topic', 'Can close topic'),
        )
    
    def __unicode__(self):
        if self.is_removed:
            return 'Topic removed'
        else:
            return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('topic', (), {'topic_id': self.id})
    
    @property
    def posts(self):
        return Post.objects.get_visible_posts().filter(topic=self)
    
    def update_posts_count(self):
        self.posts_count = self.posts.count()
    
    def update_last_post(self):
        try:
            self.last_post = self.posts.latest('date')
        except Post.DoesNotExist:
            self.last_post = None
    
    def remove(self):
        self.is_removed = True
        self.save()
    
    def restore(self):
        self.is_removed = False
        self.save()


@signals.post_save(sender=Topic)
def update_forum_on_topic_save(sender, instance, created, **kwargs):
    """
    Update forum topics, post count and last post
    """
    
    forum = instance.forum
    forum.update_topics_count()
    forum.update_posts_count()
    forum.update_last_post()
    forum.save()


class PostManager(models.Manager):
    def get_visible_posts(self):
        return self.get_query_set().filter(is_removed=False, topic__is_removed=False)

class Post(models.Model):
    date = models.DateTimeField('Post date', auto_now_add=True)
    topic = models.ForeignKey(Topic, verbose_name='Topic')
    profile = models.ForeignKey(UserProfile, verbose_name='User')
    ip_address = models.IPAddressField('IP', blank=True, null=True)
    message = models.TextField('Original bbCode message', max_length=32000)
    message_html = models.TextField('Compiled HTML message')
    is_removed = models.BooleanField('Is removed', default=False)
    
    objects = PostManager()
    
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['date']
        permissions = (
            ('move_post', 'Can move post to another topic'),
        )
    
    def __unicode__(self):
        if self.is_removed:
            return 'Post removed'
        else:
            return 'Post of %s in topic "%s"' % (self.profile, self.topic.name)
    
    @models.permalink
    def get_absolute_url(self):
        return ('post_permalink', (), {'post_id': self.id})
    
    def remove(self):
        self.is_removed = True
        self.save()
    
    def restore(self):
        self.is_removed = False
        self.save()
    
    def save(self, *args, **kwargs):
        """
        Compile bbCode message to HTML
        """
        
        self.message_html = bbcode(self.message)
        super(Post, self).save(*args, **kwargs)


@signals.post_save(sender=Post)
def update_forum_on_post_save(sender, instance, created, **kwargs):
    # Update user posts count
    profile = instance.profile
    profile.update_posts_count()
    profile.save()
    
    # Update topic posts count and last post
    topic = instance.topic
    topic.update_posts_count()
    topic.update_last_post()
    topic.save()
    
    # Update forum posts count and last post
    forum = topic.forum
    forum.update_posts_count()
    forum.update_last_post()
    forum.save()



# =============
#   Pools
# =============

class Pool(models.Model):
    topic = models.ForeignKey(Topic, verbose_name='Topic', related_name='pools')
    title = models.CharField('title', max_length=250)
    total_votes = models.PositiveIntegerField('Total votes count', default=0)
    expires = models.DateField('Pool expire date', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Pool'
        verbose_name_plural = 'Pools'
        ordering = ['id']
    
    def __unicode__(self):
        return self.title
    
    def expired(self):
        if self.expires:
            now = date.today()
            return bool(self.expires < now)
        else:
            return False
    
    def update_total_votes(self):
        self.total_votes = self.votes.count()


class PoolChoice(models.Model):
    pool = models.ForeignKey(Pool, verbose_name='Pool', related_name='choices')
    title = models.CharField('Choice', max_length=250)
    votes_count = models.PositiveIntegerField('Votes count', default=0)
    
    class Meta:
        verbose_name = 'Pool choice'
        verbose_name_plural = 'Pool choices'
        ordering = ['id']
    
    def __unicode__(self):
        return self.title
    
    def update_votes_count(self):
        self.votes_count = self.votes.count()


class PoolVote(models.Model):
    date = models.DateTimeField('Vote date', auto_now_add=True)
    profile = models.ForeignKey(UserProfile, verbose_name='User')
    pool = models.ForeignKey(Pool, verbose_name='Pool', related_name='votes')
    choice = models.ForeignKey(PoolChoice, verbose_name='Pool choice', related_name='votes')
    
    class Meta:
        verbose_name = 'Pool vote'
        verbose_name_plural = 'Pool votes'
        ordering = ['-id']


@signals.post_save(sender=PoolVote)
@signals.post_delete(sender=PoolVote)
def update_pool_on_poolvote_save(sender, instance, **kwargs):
    # Update pool total votes count
    pool = instance.pool
    pool.update_total_votes()
    pool.save()
    
    # Update choice votes count
    choice = instance.choice
    choice.update_votes_count()
    choice.save()


class Permission(models.Model):
    """
    Permissions for forum and user group
    """
    
    group = models.ForeignKey(Group, verbose_name=u'Forum group')
    forum = models.ForeignKey(Forum, verbose_name=u'Forum')
    
    # Group level permissions
    can_change_group_topic = models.BooleanField(u'Can change any topic', default=False)
    can_move_group_topic = models.BooleanField(u'Can move any topic', default=False)
    can_split_group_topic = models.BooleanField(u'Can split any topic', default=False)
    can_delete_group_topic = models.BooleanField(u'Can delete any topic', default=False)
    can_stick_group_topic = models.BooleanField(u'Can stick any topic', default=False)
    can_close_group_topic = models.BooleanField(u'Can close any topic', default=False)
    
    can_change_group_post = models.BooleanField(u'Can change any post', default=False)
    can_move_group_post = models.BooleanField(u'Can move any post', default=False)
    can_delete_group_post = models.BooleanField(u'Can delete any post', default=False)
    
    # User level permissions
    can_add_own_topic = models.BooleanField(u'Can add topics', default=False)
    can_change_own_topic = models.BooleanField(u'Can change own topic', default=False)
    can_delete_own_topic = models.BooleanField(u'Can delete own topic', default=False)
    can_close_own_topic = models.BooleanField(u'Can close own topic', default=False)
    
    can_add_own_post = models.BooleanField(u'Can add posts', default=False)
    can_change_own_post = models.BooleanField(u'Can chage own post', default=False)
    can_delete_own_post = models.BooleanField(u'Can delete own post', default=False)
    
    class Meta:
        verbose_name = u'Permission'
        verbose_name_plural = u'Permissions'
        ordering = ['forum']
        unique_together = ('group', 'forum',)
    
    def _has_priority(self, owner_profile, user_profile):
        """
        Returns True, if one user (user_profile) forum group priority is higher
        than the other (owner_profile)

        Used as an additional level of protection for higher priority group
        """
        
        if owner_profile.forum_group.priority <= user_profile.forum_group.priority:
            return True
        else:
            return False
    
    def can_add_topic(self):
        """
        User can add new topic only if he has specified permission
        """
        
        return self.can_add_own_topic
    
    def can_change_topic(self, user, topic):
        """
        Any topic can only be edited by the users, that have group permissions
        higher or equal to those of the user, who created this topic.

        Only the users that are permitted to edit their own topics would be
        able to edit their topics and the first posts in these topics.
        """
        
        if self.can_change_group_topic:
            return self._has_priority(topic.first_post.profile, user.get_profile())
        
        is_author = bool(topic.first_post.profile.user == user)
        if is_author and self.can_change_own_topic:
            return True
        
        return False
    
    def can_move_topic(self, user, topic):
        """

        Переместить любую тему может пользователь с правами группы, в которую входит
        пользователь ее создавший.
        """
        
        if self.can_move_group_topic:
            return self._has_priority(topic.first_post.profile, user.get_profile())
    
    def can_split_topic(self, user, topic):
        """
        Расщепить любую тему может пользователь с правами группы, в которую входит
        пользователь ее создавший.
        """
        
        if self.can_split_group_topic:
            return True
    
    def can_stick_topic(self, user, topic):
        """
        Закрепить любую тему может пользователь с правами группы, в которую входит
        пользователь ее создавший.
        """
        
        if self.can_stick_group_topic:
            return self._has_priority(topic.first_post.profile, user.get_profile())
    
    def can_close_topic(self, user, topic):
        """
        Закрыть любую тему может пользователь с правами уровня группы, в которую входит
        пользователь ее создавший. Свою тему - любой пользователь с правами на закрытие собственных тем.
        """
        
        if self.can_close_group_topic:
            return self._has_priority(topic.first_post.profile, user.get_profile())
        
        is_author = bool(topic.first_post.profile.user == user)
        if is_author and self.can_close_own_topic:
            return True
        
        return False
    
    def can_delete_topic(self, user, topic):
        """
        Удалить любую тему может пользователь с правами уровня группы, в которую входит
        пользователь ее создавший. Свою тему - любой пользователь с правами на удаление
        собственных тем при условии, что она пуста (за исключением первого сообщения).
        """
        
        if self.can_delete_group_topic:
            return self._has_priority(topic.first_post.profile, user.get_profile())
        
        is_author = bool(topic.first_post.profile.user == user)
        if is_author and (topic.posts_count == 1) and self.can_delete_own_topic:
            return True
        
        return False
    
    def can_add_post(self, topic):
        """
        User can add new post if he has specified permission and topic not closed
        """
        
        return self.can_add_own_post and not topic.is_closed
    
    def can_change_post(self, user, post):
        """
        Редактировать любое сообщение может пользователь с правами уровня группы, в которую входит
        пользователь его создавший. Свои сообщения - пользователь с правами на редактирование
        своих сообщений при условии, что сообщение последнее в теме.
        """
        
        if self.can_change_group_post:
            return self._has_priority(post.profile, user.get_profile())
        
        is_author = bool(post.profile.user == user)
        if is_author and (post.topic.last_post == post) and self.can_change_own_post:
            return True
        
        return False
    
    def can_move_post(self, user, topic):
        """
        Расщепить любую тему может пользователь с правами группы, в которую входит
        пользователь ее создавший.
        """
        
        return self.can_move_group_post
    
    def can_delete_post(self, user, post):
        """
        Удалить любое сообщение может пользователь с правами уровня группы, в которую входит
        пользователь его создавший. Свои сообщения - пользователь с правами на удаление своих
        сообщений при условии, что сообщение последнее в теме.
        """
        
        if self.can_delete_group_post:
            return self._has_priority(post.profile, user.get_profile())
        
        is_author = bool(post.profile.user == user)
        if is_author and (post.topic.last_post == post) and self.can_delete_own_post:
            return True
        
        return False


# ==============================
#   User related models
# ==============================

class ReadTracking(models.Model):
    """
    Forum read tracker
    
    last_read saves serialized dictionary of pairs `topic id` -> `last read post id`
    """
    
    profile = models.OneToOneField(UserProfile)
    last_read = SerializedField(blank=True)


@signals.post_save(sender=UserProfile)
def create_readtracking_on_userprofile_create(sender, instance, created, **kwargs):
    if created:
        instance.forum_group = Group.default_group()
        instance.save()
        
        ReadTracking.objects.create(profile=instance)


class SubscriptionManager(models.Manager):
    def load_related(self):
        """
        Load related objects using 1 sql query instead of len(qs) queries
        """
        qs = self.get_query_set()
        return load_content_objects(qs, cache_field='object', field='object_id', ct_field='content_type')

class Subscription(models.Model):
    """
    Subscription objects list
    """
    
    date = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(UserProfile, related_name='forum_subscription')
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id')
    
    objects = SubscriptionManager()
