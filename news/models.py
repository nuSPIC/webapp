from django.conf import settings
from django.db import models
from django.utils.html import escape


class News(models.Model):
    pub_date = models.DateField('Date published')
    title = models.CharField(max_length=250)
    content = models.TextField(help_text='Use %s tag to separate news summary' % escape(settings.CUT_TAG))

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'
        ordering = ['-pub_date', '-id']

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('news_single', (), {'news_id': self.id})

    def summary(self):
        """
        Returns news summary, text before `cut` tag
        """
        return self.content.split(settings.CUT_TAG)[0].strip()
