from django import template
from django.core.paginator import Page

register = template.Library()

@register.inclusion_tag('partials/smart_pagination.html')
def smart_pagination(page_obj, target_id="#content", pages_around=2):
    """
    Template tag para renderizar paginación inteligente
    
    Usage:
        {% load pagination_tags %}
        {% smart_pagination page_obj "#tabla-usuarios" %}
        {% smart_pagination page_obj "#products-list" 3 %}
    """
    if not isinstance(page_obj, Page):
        return {'show_pagination': False}
    
    paginator = page_obj.paginator
    current_page = page_obj.number
    
    page_range_start = max(1, current_page - pages_around)
    page_range_end = min(paginator.num_pages, current_page + pages_around)
    
    total_pages_to_show = (pages_around * 2) + 1
    if page_range_end - page_range_start < total_pages_to_show - 1:
        if page_range_start == 1:
            page_range_end = min(paginator.num_pages, page_range_start + total_pages_to_show - 1)
        else:
            page_range_start = max(1, page_range_end - total_pages_to_show + 1)
    
    return {
        'show_pagination': True,
        'page_obj': page_obj,
        'target_id': target_id,
        'custom_page_range': range(page_range_start, page_range_end + 1),
        'show_first': page_range_start > 1,
        'show_last': page_range_end < paginator.num_pages,
        'show_first_ellipsis': page_range_start > 2,
        'show_last_ellipsis': page_range_end < paginator.num_pages - 1,
    }
