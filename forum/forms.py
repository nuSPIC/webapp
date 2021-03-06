from django import forms
from django.forms.models import inlineformset_factory

from .models import Group, Topic, Post, Poll, PollChoice
from .inform import inform_new_topic

from itertools import groupby


class TopicForm(forms.ModelForm):
    name = forms.CharField(label=u'Name', required=True)

    class Meta:
        model = Topic
        fields = ('name',)

class TopicMoveForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('forum',)

    def as_div(self):
        return self._html_output(u'<div class="fieldWrapper">%(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'<span class="help_text">%s</span>', False)

    def save(self, commit=True):
        """
        Recalculate the number of posts and topics in the source and
        destination forums when a topic is moved
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
            raise forms.ValidationError(u'Not allowed to move all posts to the new topic')

        return self.cleaned_data

    def save(self):
        # Create the new topic
        new_topic = Topic(forum=self.topic.forum, name=self.cleaned_data['name'])
        new_topic.save()

        # Move posts to the new topic
        self.topic.posts.filter(pk__in=self.cleaned_data['posts']).update(topic=new_topic)

        # Update the new topic stats
        new_topic.first_post = new_topic.posts.order_by('date')[0]
        new_topic.update_posts_count()
        new_topic.update_last_post()
        new_topic.save()

        # Update the old topic stats
        self.topic.first_post = self.topic.posts.order_by('date')[0]
        self.topic.update_posts_count()
        self.topic.update_last_post()
        self.topic.save()

        # Inform subscribed users about the new topic
        inform_new_topic(new_topic)

        return new_topic


class PostMoveForm(forms.Form):
    topic_dest = forms.ChoiceField()
    posts = forms.MultipleChoiceField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.topic_src = kwargs.pop('topic_src')
        super(PostMoveForm, self).__init__(*args, **kwargs)

        # Create the topic list based on user permissions
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

        # Create the list of posts
        posts = self.topic_src.posts.order_by('date').select_related('profile', 'profile__user', 'profile__group', 'topic', 'topic__first_post')
        self.fields['posts'].choices = [(post.id, post) for post in posts]

    def clean(self):
        if not self.cleaned_data.has_key('posts'):
            raise forms.ValidationError(u'Posts to move not selected')

        if len(self.cleaned_data['posts']) == len(self.fields['posts'].choices):
            raise forms.ValidationError(u'Not allowed to move all posts to another topic')

        return self.cleaned_data

    def save(self):
        # Get the destination topic
        topic_dest_pk = self.cleaned_data['topic_dest']
        topic_dest = Topic.objects.get(pk=topic_dest_pk)

        # Move the posts to the destination topic
        self.topic_src.posts.filter(pk__in=self.cleaned_data['posts']).update(topic=topic_dest)

        # Update the stats of the destination topic
        topic_dest.first_post = topic_dest.posts.order_by('date')[0]
        topic_dest.update_posts_count()
        topic_dest.update_last_post()
        topic_dest.save()

        # Update the stats of the source topic
        self.topic_src.first_post = self.topic_src.posts.order_by('date')[0]
        self.topic_src.update_posts_count()
        self.topic_src.update_last_post()
        self.topic_src.save()

        return topic_dest


class PostForm(forms.ModelForm):
    message = forms.CharField(label=u'', widget=forms.Textarea(attrs={'class': 'bbcode fade'}))

    class Meta:
        model = Post
        fields = ('message',)

    def as_div(self):
        return self._html_output(u'<div class="fieldWrapper">%(label)s %(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'<span class="help_text">%s</span>', False)


class PollChoiceForm(forms.ModelForm):
    class Meta:
        model = PollChoice
        fields = ('title',)

PollChoiceFormset = inlineformset_factory(Poll, PollChoice, fk_name='poll', form=PollChoiceForm, can_delete=False, max_num=10, extra=10)

class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ('title', 'expires',)

    expires = forms.DateField(required=False, widget=forms.DateInput())

    def __init__(self, *args, **kwargs):
        super(PollForm, self).__init__(*args, **kwargs)
        params = {'prefix': self.prefix}
        if self.instance: params['instance'] = self.instance
        if self.data: params['data'] = self.data
        self.choice_formset = PollChoiceFormset(**params)

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
        form_valid = super(PollForm, self).is_valid()
        choices_valid = self.choice_formset.is_valid()

        return form_valid and choices_valid

    def save(self, commit=True):
        # Don't allow to edit poll with votes
        if self.instance and self.instance.total_votes > 0:
            return self.instance

        poll = super(PollForm, self).save(commit)
        self.choice_formset.instance = poll
        return poll

    def save_choices(self):
        self.choice_formset.full_clean()
        poll = self.choice_formset.instance
        for form in self.choice_formset.forms:
            if form.cleaned_data:
                form.cleaned_data['poll'] = poll
        self.choice_formset.save()



class ForumSearchForm(forms.Form):
    """
    Forum search form
    """

    term = forms.CharField(label='', min_length=1, required=True, widget=forms.TextInput(attrs={'class': 'search_term search-query', 'placeholder': 'Search'}))
