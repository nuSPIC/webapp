# coding: utf-8

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.http import base36_to_int, int_to_base36

from accounts.forms import ProfileEditForm, UserRegistrationForm
from accounts.tokens import registration_token_generator
from lib.decorators import render_to


@render_to('registration/registration_form.html')
def registration(request):
    """
    Register new user and send email with activation link
    """
    
    if request.POST:
        user_form = UserRegistrationForm(request.POST, prefix='user_form')
        profile_form = ProfileEditForm(request.POST, prefix='profile_form')
        if user_form.is_valid() and profile_form.is_valid():
            # Create new inactive user
            user = user_form.save()
            user.is_active = False
            user.save()
            
            # Fill user profile with data from registration form
            profile = user.get_profile()
            profile_form = ProfileEditForm(request.POST, instance=profile, prefix='profile_form')
            profile_form.save()
            
            # Send email with activation key to the user
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            
            context = {
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': registration_token_generator.make_token(user),
                'protocol': 'http',
                'expire': settings.REGISTRATION_TIMEOUT_DAYS,
            }
            
            subject = u'Registration confirmation on %s' % site_name
            message = render_to_string('registration/registration_email.txt', context)
            user.email_user(subject, message)
            
            return HttpResponseRedirect(reverse('registration_done'))
    else:
        user_form = UserRegistrationForm(prefix='user_form')
        profile_form = ProfileEditForm(prefix='profile_form')
    
    return {
        'user_form': user_form,
        'profile_form': profile_form,
    }


def registration_confirm(request, uidb36, token):
    """
    Check the hash in a link the user clicked and activate account
    """
    
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        user = None
    
    if (user is not None) and registration_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponseRedirect(reverse('registration_complete'))
    else:
        return HttpResponseRedirect(reverse('registration_failed'))
