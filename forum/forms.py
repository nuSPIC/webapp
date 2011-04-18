# coding: utf-8

from django import forms
from django.forms.models import inlineformset_factory

from forum.models import Group, Topic, Post, Pool, PoolChoice
from forum.inform import inform_new_topic

from itertools import groupby

__all__ = ('TopicForm', 'TopicMoveForm', 'TopicSplitForm', 'PostForm', 'PostMoveForm', 'PoolChoiceForm', 'PoolForm',)


class TopicForm(forms.ModelForm):
    name = forms.CharField(label=u'Name', required=True)
    
    class Meta:
        model = Topic
        fields = ('name',)
    
    def as_div(self):
        return self._html_output(u'<div class="field-wrapper">%(label)s %(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'<span class="help_text">%s</span>', False)


class TopicMoveForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('forum',)
    
    def as_div(self):
        return self._html_output(u'<div class="field-wrapper">%(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'<span class="help_text">%s</span>', False)
    
    def save(self, commit=True):
        """
        Recalculation posts and topics count on topic move
        in the source and destination forums
        """
        
        topic = super(TopicMoveForm, self).save(commit)
        inform_new_topic(topic)
        
        return topic


class TopicSplitForm(forms.Form):
    name = forms.CharField(label=u'New topic name')
    posts = forms.MultipleChoiceField()
    
    def __init__(self, *args, **kwargs):
        self.topic = kwargs.pop('topic')
        super(TopicSplitForm, self).__init__(*args, **kwargs)
        
        posts = self.topic.posts.order_by('date').select_related('profile', 'profile__user', 'profile__group', 'topic', 'topic__first_post')
        self.fields['posts'].choices = [(post.id, post) for post in posts]
    
    def clean(self):
        if not self.cleaned_data.has_key('posts'):
            raise forms.ValidationError(u'Posts to move not selected')
        
        if len(self.cleaned_data['posts']) == len(self.fields['posts'].choices):
            raise forms.ValidationError(u'Not allowed to move all posts to new topic')
        
        return self.cleaned_data
    
    def save(self):
        # Create new topic
        new_topic = Topic(forum=self.topic.forum, name=self.cleaned_data['name'])
        new_topic.save()
        
        # Move posts to new topic
        self.topic.posts.filter(pk__in=self.cleaned_data['posts']).update(topic=new_topic)
        
        # Update new topic stats
        new_topic.first_post = new_topic.posts.order_by('date')[0]
        new_topic.update_posts_count()
        new_topic.update_last_post()
        new_topic.save()
        
        # Update old topic stats
        self.topic.first_post = self.topic.posts.order_by('date')[0]
        self.topic.update_posts_count()
        self.topic.update_last_post()
        self.topic.save()
        
        # Inform subscribed to forum users about new topic
        inform_new_topic(new_topic)
        
        return new_topic


class PostMoveForm(forms.Form):
    topic_dest = forms.ChoiceField()
    posts = forms.MultipleChoiceField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.topic_src = kwargs.pop('topic_src')
        super(PostMoveForm, self).__init__(*args, **kwargs)
        
        # Create topic list based on user permissions
        group = Group.group_for_user(self.user)
        visible_forums_ids = list(group.permission_set.values_list('forum_id', flat=True))
        topic_list = Topic.objects.get_visible_topics().filter(forum__in=visible_forums_ids).order_by('forum__priority', 'name')
        
        topic_dest_choices = []
        for forum, topics in groupby(topic_list, lambda obj: obj.forum):
            topic_dest_choices.append(
                (forum.name,
                    [(topic.id, topic) for topic in topics]
                )
            )
        self.fields['topic_dest'].choices = topic_dest_choices
        
        # Create posts list
        posts = self.topic_src.posts.order_by('date').select_related('profile', 'profile__user', 'profile__group', 'topic', 'topic__first_post')
        self.fields['posts'].choices = [(post.id, post) for post in posts]
    
    def clean(self):
        if not self.cleaned_data.has_key('posts'):
            raise forms.ValidationError(u'Posts to move not selected')
        
        if len(self.cleaned_data['posts']) == len(self.fields['posts'].choices):
            raise forms.ValidationError(u'Not allowed to move all posts to another topic')
        
        return self.cleaned_data
    
    def save(self):
        # Get destination topic
        topic_dest_pk = self.cleaned_data['topic_dest']
        topic_dest = Topic.objects.get(pk=topic_dest_pk)
        
        # Move posts to destination topic
        self.topic_src.posts.filter(pk__in=self.cleaned_data['posts']).update(topic=topic_dest)
        
        # Update stats of destination topic
        topic_dest.first_post = topic_dest.posts.order_by('date')[0]
        topic_dest.update_posts_count()
        topic_dest.update_last_post()
        topic_dest.save()
        
        # Update stats of source topic
        self.topic_src.first_post = self.topic_src.posts.order_by('date')[0]
        self.topic_src.update_posts_count()
        self.topic_src.update_last_post()
        self.topic_src.save()
        
        return topic_dest


class PostForm(forms.ModelForm):
    message = forms.CharField(label=u'', widget=forms.Textarea(attrs={'class': 'resizable bbcode', 'rows': 15}))
    
    class Meta:
        model = Post
        fields = ('message',)
    
    def as_div(self):
        return self._html_output(u'<div class="field-wrapper">%(label)s %(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'<span class="help_text">%s</span>', False)


class PoolChoiceForm(forms.ModelForm):
    class Meta:
        model = PoolChoice
        fields = ('title',)

PoolChoiceFormset = inlineformset_factory(Pool, PoolChoice, fk_name='pool', form=PoolChoiceForm, can_delete=False, max_num=10, extra=10)

class PoolForm(forms.ModelForm):
    class Meta:
        model = Pool
        fields = ('title', 'expires',)
    
    expires = forms.DateField(required=False, widget=forms.DateInput())
    
    def __init__(self, *args, **kwargs):
        super(PoolForm, self).__init__(*args, **kwargs)
        params = {'prefix': self.prefix}
        if self.instance: params['instance'] = self.instance
        if self.data: params['data'] = self.data
        self.choice_formset = PoolChoiceFormset(**params)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        empty = True
        self.choice_formset.is_valid()
        for form in self.choice_formset.forms:
            if form.cleaned_data:
                empty = False
                break
        
        if empty:
            raise forms.ValidationError(u'You must select at least one choice')
        
        return cleaned_data
    
    def is_valid(self):
        form_valid = super(PoolForm, self).is_valid()
        choices_valid = self.choice_formset.is_valid()
        
        return form_valid and choices_valid
    
    def save(self, commit=True):
        # Don't allow to edit pool with votes
        if self.instance and self.instance.total_votes > 0:
            return self.instance
        
        pool = super(PoolForm, self).save(commit)
        self.choice_formset.instance = pool
        return pool
    
    def save_choices(self):
        self.choice_formset.full_clean()
        pool = self.choice_formset.instance
        for form in self.choice_formset.forms:
            if form.cleaned_data:
                form.cleaned_data['pool'] = pool
        self.choice_formset.save()
