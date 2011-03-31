# coding: utf-8

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.http import base36_to_int

from accounts.forms import RegistrationForm
from accounts.tokens import registration_token_generator
from lib.decorators import render_to


@render_to('registration/registration_form.html')
def registration(request):
    """
    Register new user and send email with activation link
    """
    
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save(request)
            return HttpResponseRedirect(reverse('registration_done'))
    else:
        form = RegistrationForm()
    
    return {
        'form': form,
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
