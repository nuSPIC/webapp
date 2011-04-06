# coding: utf-8

from django.conf import settings
from django.template import Library


register = Library()

@register.inclusion_tag('templatetags/pagination.html')
def pagination(page, objects_caption, query_string=''):
    """
    Render pages navigation block.
    
    page            - instance of :model:`django.core.paginator.Page` returned by `lib.helpers.paginate_by` method
    objects_caption - stores the caption that is displayed next to the amount of objects
    query_string    - query string as a string argument (data of type application/x-www-form-urlencoded), joined to
                      every link as additional query parameter
    """
    
    if not page.has_other_pages():
        return {
            'page_object': page,
        }
    
    padding = settings.PAGINATION_PADDING
    tail = settings.PAGINATION_TAIL
    
    current_page = page.number
    pages_count = page.paginator.num_pages + 1
    
    # Create a list of pages which are within +/- `padding` items around the current one
    main_range_from = max(current_page - padding, 1)
    main_range_to = min(main_range_from + padding * 2 + 1, pages_count)
    main_range = range(main_range_from, main_range_to)
    
    # Create a list of `tail` pages located at the beginning of the navigation block
    left_range_from = 1
    left_range_to = min(left_range_from + tail, main_range_from)
    left_range = range(left_range_from, left_range_to)
    
    # If the lists main_range and left_range overlap, join them
    # to avoid a discontinuity in the navigation block
    if (main_range[0] - 1) <= tail:
        main_range = left_range + main_range
        left_range = []
    
    # Same for the right side of the navigation block
    right_range_to = pages_count
    right_range_from = max(right_range_to - tail, main_range_to)
    right_range = range(right_range_from, right_range_to)
    
    if (main_range[-1] + 1) >= (pages_count - tail):
        main_range = main_range + right_range
        right_range = []
    
    if query_string:
        query_string = '&' + query_string
    
    return {
        'left_range': left_range,
        'main_range': main_range,
        'right_range': right_range,
        'page': page,
        'query_string': query_string,
        'objects_caption': objects_caption,
    }
