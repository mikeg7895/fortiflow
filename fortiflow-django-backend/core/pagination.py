from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math

class ElidedPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100     

    def get_displayed_page_numbers(self, current_page, total_pages):
        pages = set()

        for i in range(1, 3):
            if 1 <= i <= total_pages:
                pages.add(i)

        for i in range(total_pages - 1, total_pages + 1):
            if 1 <= i <= total_pages:
                pages.add(i)

        for i in range(current_page - 2, current_page + 3):
            if 1 <= i <= total_pages:
                pages.add(i)

        return sorted(pages)

    def get_paginated_response(self, data):
        total = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        total_pages = math.ceil(total / page_size) if page_size else 1
        current_page = self.page.number

        visible_pages = self.get_displayed_page_numbers(current_page, total_pages)

        return Response({
            'count': total,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page': current_page,
            'total_pages': total_pages,
            'visible_pages': visible_pages,
            'results': data
        })
