# coding: utf-8

from django import forms
from django.contrib import admin

from accounts.models import Group
from forum.models import Forum, Topic, Permission, Post, Pool, PoolChoice, PoolVote



class GroupAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'member_title', 'slug', 'priority', 'is_default', 'is_anonymous',)}),
    )
    list_display = ('title', 'member_title', 'is_default', 'is_anonymous', 'slug', 'priority',)
    list_display_links = ('title', 'member_title',)
    ordering = ('-priority',)

admin.site.register(Group, GroupAdmin)


class ForumAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'description', 'priority',)}),
    )
    list_display = ('name', 'description', 'priority', 'topics_count', 'posts_count',)
    list_display_links = ('name',)
    ordering = ('priority',)

admin.site.register(Forum, ForumAdmin)


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
    
    def save(self, commit=True):
        """
        Remove or restore topic on is_removed flag changing
        """
        
        topic = super(TopicForm, self).save(commit=True)
        
        if 'is_removed' in self.changed_data:
            if topic.is_removed:
                topic.remove()
            else:
                topic.restore()
        
        return topic

class TopicAdmin(admin.ModelAdmin):
    form = TopicForm
    
    fieldsets = (
        (None, {'fields': ('forum', 'name', 'is_sticked', 'is_closed', 'is_removed',)}),
    )
    list_display = ('forum', 'name', 'posts_count', 'is_sticked', 'is_closed', 'is_removed',)
    list_display_links = ('name',)
    list_filter = ('is_sticked', 'is_closed', 'is_removed',)
    raw_id_fields = ('forum',)
    ordering = ['-id']

admin.site.register(Topic, TopicAdmin)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
    
    def save(self, commit=True):
        """
        Remove or restore post on is_removed flag changing
        """
        
        post = super(PostForm, self).save(commit=True)
        
        if 'is_removed' in self.changed_data:
            if post.is_removed:
                post.remove()
            else:
                post.restore()
        
        return post

class PostAdmin(admin.ModelAdmin):
    def queryset(self, request):
        return self.model._default_manager.select_related('profile', 'profile__user', 'topic', 'topic__name')
    
    form = PostForm
    
    fieldsets = (
        (None, {'fields': ('topic', 'profile', 'ip_address', 'message', 'message_html', 'is_removed',)}),
    )
    list_display = ('date', 'topic', 'profile', 'ip_address', 'is_removed',)
    list_display_links = ('topic',)
    list_filter = ('is_removed',)
    raw_id_fields = ('topic', 'profile',)
    search_fields = ('profile__user__username', 'topic__name',)
    ordering = ['-date']

admin.site.register(Post, PostAdmin)


class PoolChoiceInline(admin.TabularInline):
    def queryset(self, request):
        return self.model._default_manager.select_related('pool')
    
    model = PoolChoice
    
    fieldsets = (
        (None, {'fields': ('pool', 'title', 'votes_count',)}),
    )
    list_display = ('pool', 'title', 'votes_count',)
    list_display_links = ('pool', 'title',)
    raw_id_fields = ('pool',)
    search_fields = ( 'pool__title', 'title',)
    ordering = ['-id']

class PoolAdmin(admin.ModelAdmin):
    def queryset(self, request):
        return self.model._default_manager.select_related('topic')
    
    inlines = [PoolChoiceInline,]
    
    fieldsets = (
        (None, {'fields': ('topic', 'title', 'total_votes', 'expires',)}),
    )
    list_display = ('topic', 'title', 'total_votes', 'expires',)
    list_display_links = ('topic', 'title',)
    raw_id_fields = ('topic',)
    search_fields = ( 'topic__name', 'title',)
    ordering = ['-id']

admin.site.register(Pool, PoolAdmin)


class PoolVoteAdmin(admin.ModelAdmin):
    def queryset(self, request):
        return self.model._default_manager.select_related('profile', 'profile__user', 'pool', 'choice',)
    
    fieldsets = (
        (None, {'fields': ('profile', 'pool', 'choice',)}),
    )
    list_display = ('date', 'profile', 'pool', 'choice',)
    list_display_links = ('profile', 'pool',)
    raw_id_fields = ('profile', 'pool', 'choice')
    search_fields = ( 'profile__user__username', 'pool__title', 'choice__title',)
    ordering = ['-date']

admin.site.register(PoolVote, PoolVoteAdmin)


class PermissionAdmin(admin.ModelAdmin):
    def queryset(self, request):
        return self.model._default_manager.select_related('group', 'forum')
    
    fieldsets = (
        (u'Permission assignment objects', {'fields': ('group', 'forum',)}),
        (u'Group level permissions',
            {'fields': ('can_change_group_topic', 'can_move_group_topic', 'can_split_group_topic', 'can_delete_group_topic',
                        'can_stick_group_topic', 'can_close_group_topic', 'can_change_group_post', 'can_move_group_post',
                        'can_delete_group_post',)}),
        (u'User level permissions',
            {'fields': ('can_add_own_topic', 'can_change_own_topic', 'can_delete_own_topic', 'can_close_own_topic',
                        'can_add_own_post', 'can_change_own_post', 'can_delete_own_post',)}),
    )
    list_display = ('group', 'forum',)
    list_display_links = ('group', 'forum',)
    list_filter = ('group', 'forum',)
    ordering = ('forum',)

admin.site.register(Permission, PermissionAdmin)
