# coding: utf-8

from django.contrib import admin

from accounts.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (u'Associated account', {'fields': ('user',)}),
        (u'Profile information', {'fields': ('academic_affiliation', 'public_email', 'web_page', 'notes',)}),
        (u'Forum', {'fields': ('forum_group', 'forum_email_notification',)}),
    )
    list_display = ('user', 'academic_affiliation', 'public_email',)
    ordering = ('-id',)
    search_fields = ('user__username',)
    raw_id_fields = ('user',)

admin.site.register(UserProfile, UserProfileAdmin)
