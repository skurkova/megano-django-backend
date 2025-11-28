from django.db import models
from django.conf import settings

from products.models import Product


class BasketItem(models.Model):
    """Модель BasketItem представляет собой продукт в корзине и его количество"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    """Модель Order представляет собой заказ"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, db_index=True)
    createdAt = models.DateTimeField(auto_now_add=True, db_index=True)
    fullName = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    deliveryType = models.CharField(max_length=20, default='ordinary')
    paymentType = models.CharField(max_length=20, default='online')
    totalCost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='created')
    city = models.CharField(max_length=30)
    address = models.TextField()
    is_deleted = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f'Order {self.pk} by user {self.user}'


class OrderProduct(models.Model):
    """
    Модель OrderProduct представляет собой продукт в заказе
    count - количество товара в корзине
    price - их общая цена на момент покупки
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Product in order №{self.order}'


class Payment(models.Model):
    """Модель Payment представляет собой оплату заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_index=True)
    number = models.CharField(max_length=8)
    name = models.CharField(max_length=200)
    month = models.CharField(max_length=2)
    year = models.CharField(max_length=4)
    code = models.CharField(max_length=3)

    def __str__(self):
        return f'Payment for order №{self.order}'


class DeliveryType(models.Model):
    """Модель Delivery представляет собой тип доставки"""
    cost_ordinary_delivery = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)
    cost_express_delivery = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    min_cost_order_by_free_delivery = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)

    def __str__(self):
        return 'Delivery type'
