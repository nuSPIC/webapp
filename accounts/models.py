# coding: utf-8

from django.contrib.auth.models import User
from django.db import models

from lib.decorators import signals


class Group(models.Model):
    """
    Forum group
    """
    
    title = models.CharField(u'Group title', max_length=30)
    member_title = models.CharField(u'Member title', max_length=30)
    slug = models.SlugField(u'Group slug', max_length=50)
    priority = models.PositiveSmallIntegerField(u'Priority', default=0)
    is_default = models.BooleanField(u'Is default for registered users', default=False)
    is_anonymous = models.BooleanField(u'Is default for anonymous users', default=False)
    
    class Meta:
        verbose_name = u'Forum group'
        verbose_name_plural = u'Forum groups'
    
    def __unicode__(self):
        return self.title
    
    @classmethod
    def default_group(cls):
        try:
            return cls.objects.get(is_default=True)
        except Group.DoesNotExist:
            return None
    
    @classmethod
    def anonymous_group(cls):
        try:
            return cls.objects.get(is_anonymous=True)
        except Group.DoesNotExist:
            return None

    @classmethod
    def group_for_user(cls, user):
        if user.is_authenticated():
            return user.get_profile().forum_group
        else:
            return cls.anonymous_group()


class UserProfile(models.Model):
    """
    User profile stores additional user information
    """
    
    OCCUPATIONS = (
        (0, 'Unspecified'),
        (1, 'High school'),
        (2, 'University'),
        (3, 'Industry'),
        (4, 'Other'),
    )
    
    user = models.OneToOneField(User, related_name='profile')
    present_occupation = models.SmallIntegerField('Present occupation', choices=OCCUPATIONS, default=0)
    academic_affiliation = models.CharField('Present academic affiliation', max_length=150, blank=True)
    public_email = models.EmailField('Public e-mail address', blank=True)
    web_page = models.URLField('Publicly visible web page address', verify_exists=False, blank=True)
    notes = models.TextField('Miscellaneous notes', max_length=1500, blank=True)
    
    forum_group = models.ForeignKey(Group, verbose_name=u'Forum group', blank=True, null=True)
    post_count = models.PositiveIntegerField(u'Forum posts count', default=0)
    forum_email_notification = models.BooleanField(u'Notify by email about updates in subscribed topics and forums', default=True)
    
    ip_address  = models.IPAddressField(u'IP Address', blank=True, null=True)
    last_email_request = models.DateTimeField('Last e-mail request', blank=True, null=True)
    temporary_email = models.EmailField('Field for temporary storage of the new primary e-mail', blank=True)
    
    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'User profiles'
        ordering = ['-id']
    
    def __unicode__(self):
        return self.user.username
    
    @models.permalink
    def get_absolute_url(self):
        return ('profile', (), {'profile_id': self.id})
    
    def update_posts_count(self):
        self.post_count = self.post_set.get_visible_posts().count()


@signals.post_save(sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create associated user profile when a new user is created
    """
    if created:
        UserProfile.objects.create(user=instance)
