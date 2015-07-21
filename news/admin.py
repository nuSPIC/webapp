from django.contrib import admin

from .models import News


class NewsAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    fields = ('pub_date', 'title', 'content',)
    list_display = ('pub_date', 'title',)
    list_display_links = ('title',)

admin.site.register(News, NewsAdmin)
