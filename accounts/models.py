# coding: utf-8

from django.contrib.auth.models import User
from django.db import models

from lib.decorators import signals


class UserProfile(models.Model):
    """
    User profile stores additional user information
    """
    
    user = models.OneToOneField(User, related_name='profile')
    academic_affiliation = models.CharField('Present academic affiliation', max_length=150, blank=True)
    public_email = models.EmailField('Public e-mail address', blank=True)
    web_page = models.URLField('Publicly visible web page address', verify_exists=False, blank=True)
    notes = models.TextField('Miscellaneous notes', max_length=1500, blank=True)
    
    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'User profiles'
        ordering = ['-id']
    
    def __unicode__(self):
        return self.user.username


@signals.post_save(sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create associated user profile when new user created
    """
    if created:
        UserProfile.objects.create(user=instance)
