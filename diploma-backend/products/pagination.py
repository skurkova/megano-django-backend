from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """Пользовательская пагинация страниц"""
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100
    page_query_param = 'currentPage'          # как в OpenAPI

    def get_paginated_response(self, data):
        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': self.page.paginator.num_pages,
        })
