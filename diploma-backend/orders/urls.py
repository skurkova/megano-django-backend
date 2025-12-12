from django.urls import path

from .views import OrderAPIView, OrdersAPIView, BasketAPIView, PaymentAPIView

app_name = 'orders'

urlpatterns = [
    path('basket', BasketAPIView.as_view(), name='basket'),
    path('order/<int:pk>', OrderAPIView.as_view(), name='order_id'),
    path('orders', OrdersAPIView.as_view(), name='orders'),
    path('payment/<int:pk>', PaymentAPIView.as_view(), name='payment'),
]
