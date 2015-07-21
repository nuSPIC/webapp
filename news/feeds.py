from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from .models import News


# Get current site and retrieve the site name
current_site = Site.objects.get_current()
site_name = current_site.name


class NewsFeed(Feed):
    """
    Latest news
    """

    title = u'%s > News' % site_name
    description = u'Latest news from %s' % site_name

    def link(self):
        return reverse('news_archive')

    def items(self):
        return News.objects.all()[:settings.NEWS_FEED_ITEMS_COUNT]

    def item_description(self, item):
        return mark_safe(item.content)
