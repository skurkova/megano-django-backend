from django.contrib import admin
from django.db.models import QuerySet

from .models import Order, OrderProduct, DeliveryType


class OrderProductInline(admin.TabularInline):
    model = OrderProduct


@admin.action(description='Mark deleted')
def soft_delete(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    queryset.update(is_deleted=True)


@admin.action(description='Restore')
def restore(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    queryset.update(is_deleted=False)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = 'pk', 'user', 'createdAt', 'deliveryType', 'totalCost', 'is_deleted', 'city', 'address'
    list_display_links = 'pk', 'user'
    list_filter = 'user', 'createdAt', 'deliveryType', 'is_deleted', 'totalCost', 'status'
    search_fields = 'pk', 'address'
    ordering = 'pk', '-createdAt'
    inlines = [OrderProductInline]
    actions = [soft_delete, restore]

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')


@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    list_display = 'cost_ordinary_delivery', 'cost_express_delivery', 'min_cost_order_by_free_delivery'
    list_display_links = 'cost_ordinary_delivery', 'cost_express_delivery', 'min_cost_order_by_free_delivery'
