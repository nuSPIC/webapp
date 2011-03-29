# coding: utf-8

from django.conf.urls.defaults import *


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
        {'template_name': 'password_reset/password_reset_form.html', 'email_template_name': 'password_reset/password_reset_email.txt'}, 'password_reset'),
    (r'^password_reset/done/$', 'password_reset_done',
        {'template_name': 'password_reset/password_reset_done.html'}),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'password_reset_confirm',
        {'template_name': 'password_reset/password_reset_confirm.html'}),
    (r'^reset/done/$', 'password_reset_complete',
        {'template_name': 'password_reset/password_reset_complete.html'}),
)
