# coding: utf-8

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.contrib.flatpages.models import FlatPage
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.http import Http404
from django.utils.safestring import mark_safe


def get_flatpage_or_none(request):
    """
    Returns a FlatPage object of requested page or None
    """
    
    url = request.path_info
    
    try:
        fp = FlatPage.objects.get(url__exact=url, sites__id__exact=settings.SITE_ID)
    except FlatPage.DoesNotExist:
        return None
    
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if fp.registration_required and not request.user.is_authenticated():
        return redirect_to_login(request.path)
    
    # To avoid having to always use the "|safe" filter in flatpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    fp.title = mark_safe(fp.title)
    fp.content = mark_safe(fp.content)
    
    return fp


def paginate(request, objects, per_page):
    """
    Split objects into pages and returns :model:`django.core.paginator.Page` instance
    of current page, passed in request.
    """
    
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        raise Http404
    
    paginator = Paginator(objects, per_page)
    
    try:
        page = paginator.page(page)
    except (InvalidPage, EmptyPage):
        page = paginator.page(paginator.num_pages)
    
    return page
