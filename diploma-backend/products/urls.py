from django.urls import path

from .views import (
    TagListAPIView,
    CategoryListAPIView,
    ProductsPopularListAPIView,
    ProductsLimitedListAPIView,
    ProductBannersListAPIView,
    SaleListAPIView,
    ProductCatalogListAPIView,
    ProductRetrieveAPIView,
    ProductReviewCreateAPIView
)

app_name = 'products'

urlpatterns = [
    path('products/popular', ProductsPopularListAPIView.as_view(), name='products-popular'),
    path('products/limited', ProductsLimitedListAPIView.as_view(), name='products-limited'),
    path('product/<int:pk>/reviews', ProductReviewCreateAPIView.as_view(), name='product-reviews'),
    path('product/<int:pk>', ProductRetrieveAPIView.as_view(), name='product-details'),
    path('banners', ProductBannersListAPIView.as_view(), name='banners'),
    path('sales', SaleListAPIView.as_view(), name='sales'),
    path('catalog', ProductCatalogListAPIView.as_view(), name='catalog'),
    path('tags', TagListAPIView.as_view(), name='tags'),
    path('categories', CategoryListAPIView.as_view(), name='categories'),
]
