# coding: utf-8

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.contrib.contenttypes.models import ContentType
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


def load_content_objects(object_list, cache_field='content_object', field='object_id', ct_field='content_type', select_related=1):
    """
    Load content objects for a generic relation.

    Number of sql queries is equals not to number of objects but number of
    unique content types. For example we have article and project models that
    can be tagged and we want to load all objects tagged with a tag, then we
    always will spent 2 SQL queries instead of number of tagged objects SQL
    queries.

    Parameters:

     - object_list - list of objects with GenericForeignKey to process
     - cache_field - name of attribute, which should contain loaded
       object. Typically it's a name of a GenericForeignKey field.
     - field - field, which contains object_id
     - ct_field - field, which contains foreign key to content type
     
    (c) 2006-2009 Alexander Solovyov
    """
    
    if not object_list:
        return object_list
    
    field = object_list[0]._meta.get_field(field)
    ct_field = object_list[0]._meta.get_field(ct_field)
    ctypes = {}
    
    for obj in object_list:         # group objects by ctype
        ct_id = getattr(obj, ct_field.column)
        try:
            ctypes[ct_id].append(obj)
        except KeyError:
            ctypes[ct_id] = [obj]
    
    for ct_id, objects in ctypes.items(): # fetch each ctype by 1 SQL query
        ctype = ContentType.objects.get_for_id(ct_id)
        model = ctype.model_class()
        pk_field = model._meta.pk
        pk_object_map = {}
        
        for obj in objects:
            pk_value = pk_field.to_python(getattr(obj, field.column))
            try:
                pk_object_map[pk_value].append(obj)
            except KeyError:
                pk_object_map[pk_value] = [obj]
        
        keys = pk_object_map.keys()
        qs = model.objects.filter(pk__in=keys)
        
        if select_related:
            qs = qs.select_related(depth=select_related)
        
        for model_obj in qs:
            for obj in pk_object_map[model_obj.pk]:
                setattr(obj, cache_field, model_obj)
    
    return object_list
