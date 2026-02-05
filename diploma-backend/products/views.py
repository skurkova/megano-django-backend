from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

from django.db.models import Avg, Value, Count
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from .models import Tag, Category, Product, Sale, Review
from .pagination import CustomPagination
from .serializers import (
    ProductShortSerializer,
    ProductFullSerializer,
    TagSerializer,
    CategorySerializer,
    SaleSerializer,
    ReviewSerializer
)

LIMITED_COUNT_THRESHOLD = 3


class TagListAPIView(ListAPIView):
    """Получить список тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CategoryListAPIView(ListAPIView):
    """Получить список категорий"""
    queryset = Category.objects.filter(parent__isnull=True, is_deleted=False).prefetch_related('subcategories').all()
    serializer_class = CategorySerializer


class ProductsPopularListAPIView(ListAPIView):
    """Получить список популярных продуктов"""
    serializer_class = ProductShortSerializer

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related(
            'images', 'tags', 'reviews').annotate(rating=Coalesce(Avg('reviews__rate'), Value(0.00)),
                                                  reviews_count=Count('reviews')).order_by(
            '-rating', '-reviews_count').distinct()[:8]


class ProductsLimitedListAPIView(ListAPIView):
    """
    Получить список лимитированных продуктов: до 3 шт в наличии
    LIMITED_COUNT_THRESHOLD = 3
    """
    serializer_class = ProductShortSerializer

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related(
            'images', 'tags', 'reviews').annotate(rating=Coalesce(Avg('reviews__rate'), Value(0.00)),
                                                  reviews_count=Count('reviews')).filter(
            count__lte=LIMITED_COUNT_THRESHOLD, count__gt=0).distinct()[:16]


class ProductBannersListAPIView(ListAPIView):
    """Получить список продуктов для баннера"""
    serializer_class = ProductShortSerializer

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related(
            'images', 'tags', 'reviews').annotate(rating=Coalesce(Avg('reviews__rate'), Value(0.00)),
                                                  reviews_count=Count('reviews')).distinct()[:3]


class SaleListAPIView(ListAPIView):
    """Получить список продуктов со скидкой"""
    serializer_class = SaleSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Sale.objects.select_related('product').prefetch_related('product__images')


class ProductCatalogListAPIView(ListAPIView):
    """Получить список отфильтрованных продуктов"""
    serializer_class = ProductShortSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Получаем фильтры из запроса
        filters_params = self.request.query_params

        # Определяем по каким фильтрам получить продукты
        filters = {}

        # Фильтрация по категории
        category = filters_params.get('category')
        if category and category.isdigit():
            filters['category'] = int(category)

        # Фильтрация по названию
        name = filters_params.get('filter[name]')
        if name and name.strip():
            filters['title__icontains'] = name.strip()

        # Фильтрация по цене
        min_price = filters_params.get('filter[minPrice]')
        if min_price not in (None, ''):
            filters['price__gte'] = float(min_price)

        max_price = filters_params.get('filter[maxPrice]')
        if max_price not in (None, ''):
            filters['price__lte'] = float(max_price)

        # Фильтрация по бесплатной доставке
        freeDelivery = filters_params.get('filter[freeDelivery]')
        if freeDelivery == 'true':
            filters['freeDelivery'] = True

        # Фильтрация по наличию товара (count > 0)
        available = filters_params.get('filter[available]')
        if available == 'true':
            filters['count__gt'] = 0

        # Фильтрация по тегам
        tags = filters_params.getlist('tags[]')
        if len(tags) > 0:
            tag_ids = [int(tag) for tag in tags]
            filters['tags__id__in'] = tag_ids

        # Сортировка
        sort = filters_params.get('sort', default='datе')
        sort_type = filters_params.get('sortType', default='dec')

        sort_mapping = {
            'rating': 'rating',
            'price': 'price',
            'date': 'date',
            'reviews': 'reviews_count',
        }

        sort_field = sort_mapping.get(sort, 'date')

        if sort_type == 'dec':
            sort_field = f'-{sort_field}'

        return Product.objects.select_related(
            'category'
        ).prefetch_related(
            'images', 'tags'
        ).annotate(
            rating=Coalesce(Avg('reviews__rate'), Value(0.00)),
            reviews_count=Count('reviews')
        ).filter(
            **filters
        ).order_by(
            sort_field
        ).distinct()


class ProductRetrieveAPIView(RetrieveAPIView):
    """Получить полное описание продукта"""
    serializer_class = ProductFullSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related(
            'images', 'tags', 'reviews').annotate(rating=Coalesce(Avg('reviews__rate'), Value(0.00)))


class ProductReviewCreateAPIView(CreateAPIView):
    """Добавить отзыв на продукт"""
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        product = get_object_or_404(Product, id=self.kwargs['pk'])
        serializer.save(product=product)
