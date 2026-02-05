from django.contrib import admin
from django.db.models import QuerySet

from .models import Product, ProductImage, Specification, Category, Tag, Review, Sale


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class SpecificationInline(admin.TabularInline):
    model = Specification


@admin.action(description='Mark deleted')
def soft_delete(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    queryset.update(is_deleted=True)


@admin.action(description='Restore')
def restore(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    queryset.update(is_deleted=False)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title', 'parent', 'is_deleted',
    list_display_links = 'pk', 'title',
    list_filter = 'is_deleted', 'parent'
    search_fields = 'title',
    ordering = 'pk', 'title',
    actions = [soft_delete, restore]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name',
    list_display_links = 'pk', 'name',
    search_fields = 'name',
    ordering = 'pk', 'name',


class CategoryWithSubcategoriesFilter(admin.SimpleListFilter):
    title = 'Category with Subcategories'
    parameter_name = 'category_with_subcategories'

    def lookups(self, request, model_admin):
        # Показываем только корневые категории
        return [(c.id, c.title) for c in Category.objects.filter(parent__isnull=True)]

    def queryset(self, request, queryset):
        if self.value():
            category_id = self.value()
            # Получаем ID подкатегорий
            subcategory_ids = Category.objects.filter(parent_id=category_id).values_list('id', flat=True)
            # Включаем саму категорию + подкатегории
            all_category_ids = [category_id] + list(subcategory_ids)
            return queryset.filter(category_id__in=all_category_ids)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title', 'category', 'price', 'count', 'description', 'freeDelivery', 'is_deleted'
    list_display_links = 'pk', 'title',
    list_filter = 'is_deleted', 'freeDelivery', CategoryWithSubcategoriesFilter, 'tags'
    search_fields = 'title', 'description'
    ordering = 'pk', 'title'
    actions = [soft_delete, restore]
    inlines = [ProductImageInline, SpecificationInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = 'pk', 'product', 'author', 'email', 'text', 'rate', 'date'
    list_display_links = 'pk', 'product',
    list_filter = 'rate', 'product'
    search_fields = 'product__title', 'author', 'text'
    ordering = 'pk', 'date'


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = 'pk', 'product', 'salePrice', 'dateFrom', 'dateTo'
    list_display_links = 'pk', 'product',
    list_filter = 'dateFrom', 'dateTo'
    search_fields = 'product__title',
    ordering = 'pk',
