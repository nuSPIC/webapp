# coding: utf-8

from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from accounts.forms import CustomPasswordResetForm


# Django built-in user actions with custom templates
urlpatterns = patterns('django.contrib.auth.views',
    (r'^login/$', 'login',
        {'template_name': 'auth/login.html'}, 'login'),
    (r'^logout/$', 'logout',
        {'template_name': 'auth/logged_out.html'}, 'logout'),
    (r'^password_change/$', 'password_change',
        {'template_name': 'password_change/password_change_form.html'}, 'password_change'),
    (r'^password_change/done/$', 'password_change_done',
        {'template_name': 'password_change/password_change_done.html'}),
    (r'^password_reset/$', 'password_reset',
        {
            'template_name': 'password_reset/password_reset_form.html',
            'email_template_name': 'password_reset/password_reset_email.txt',
            'password_reset_form': CustomPasswordResetForm,
        }, 'password_reset'),
    (r'^password_reset/done/$', 'password_reset_done',
        {'template_name': 'password_reset/password_reset_done.html'}),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'password_reset_confirm',
        {'template_name': 'password_reset/password_reset_confirm.html'}),
    (r'^reset/done/$', 'password_reset_complete',
        {'template_name': 'password_reset/password_reset_complete.html'}),
)

urlpatterns += patterns('accounts.views',
    # Registration
    url(r'^registration/$', 'registration', name='registration'),
    url(r'^registration/done/$', direct_to_template,
        {'template': 'registration/registration_done.html'}, name='registration_done'),
    url(r'^registration/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'registration_confirm', name='registration_confirm'),
    url(r'^registration/failed/$', direct_to_template,
        {'template': 'registration/registration_failed.html', 'extra_context': {'expire': settings.REGISTRATION_TIMEOUT_DAYS}}, name='registration_failed'),
    url(r'^registration/complete/$', direct_to_template,
        {'template': 'registration/registration_complete.html'}, name='registration_complete'),
    
    # Community
    url(r'^$', 'accounts', {'sort_order': 'user__last_name'}, name='accounts'),
    url(r'^by_date/$', 'accounts', {'sort_order': ['user__date_joined', '-id']}, name='accounts_by_date'),
    
    # User profile
    url(r'^(?P<profile_id>\d+)/$', 'profile', name='profile'),
    url(r'^(?P<profile_id>\d+)/edit/$', 'profile_edit', name='profile_edit'),
    
    # Primary e-mail change
    url(r'^email_change/done/$', direct_to_template,
        {'template': 'email_change/email_change_done.html', 'extra_context': {'expire': settings.EMAIL_CHANGE_TIMEOUT_DAYS}}, name='email_change_done'),
    url(r'^email_change/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'email_change_confirm', name='email_change_confirm'),
    url(r'^email_change/complete/$', direct_to_template,
        {'template': 'email_change/email_change_complete.html'}, name='email_change_complete'),
    url(r'^email_change/failed/$', direct_to_template,
        {'template': 'email_change/email_change_failed.html', 'extra_context': {'expire': settings.EMAIL_CHANGE_TIMEOUT_DAYS}}, name='email_change_failed'),
)
