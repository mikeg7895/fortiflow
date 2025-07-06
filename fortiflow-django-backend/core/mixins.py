class SmartPaginationMixin:
    def get_pagination_context(self, page_obj, pages_around=2):
        """
        Genera el contexto para paginación inteligente
        
        Args:
            page_obj: El objeto página de Django
            pages_around: Número de páginas a mostrar alrededor de la actual (default: 2)
        """
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
            'custom_page_range': range(page_range_start, page_range_end + 1),
            'show_first': page_range_start > 1,
            'show_last': page_range_end < paginator.num_pages,
            'show_first_ellipsis': page_range_start > 2,
            'show_last_ellipsis': page_range_end < paginator.num_pages - 1,
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if context.get('is_paginated'):
            page_obj = context['page_obj']
            pagination_context = self.get_pagination_context(page_obj)
            context.update(pagination_context)
        
        return context