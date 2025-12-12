from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from django.db.models import Avg, Value, Count, Prefetch, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from .models import Order, BasketItem, OrderProduct, DeliveryType
from .serializers import OrderSerializer, PaymentSerializer, BasketItemResponseSerializer, OrderProductSerializer

from products.models import Product
from products.serializers import ProductShortSerializer


class BasketAPIView(APIView):
    """
    Действия с корзиной:
    - получить список товаров в корзине
    - добавить товары в корзину
    - удалить товар из корзины
    Для анонимных пользователей в качестве временного хранилища корзины используем сессию,
    для авторизованных - БД
    """
    permission_classes = [AllowAny]  # ← Полный доступ для всех

    def get_basket_queryset(self):
        return BasketItem.objects.prefetch_related(
            Prefetch(
                'product',
                queryset=Product.objects.select_related('category').prefetch_related(
                    'images', 'tags').annotate(rating=Coalesce(Avg('reviews__rate'), Value(0.00)),
                                               reviews_count=Count('reviews'))))

    def get_queryset_product(self):
        return Product.objects.select_related('category').prefetch_related(
                    'images', 'tags').annotate(rating=Coalesce(Avg('reviews__rate'), Value(0.00)),
                                               reviews_count=Count('reviews'))

    def get(self, request: Request) -> Response:
        if request.user.is_authenticated:
            # Корзина из БД
            basket = self.get_basket_queryset().filter(user=request.user)
            serializer_products = BasketItemResponseSerializer(basket, many=True)
            return Response(serializer_products.data, status=status.HTTP_200_OK)
        else:
            # Корзина из сессии
            basket = request.session.get('basket', [])
            products_ids = [item['product'] for item in basket]
            products = {product.id: product for product in self.get_queryset_product().filter(id__in=products_ids)}

            serializer_products = []
            for item in basket:
                product = products.get(item['product'])
                product.count = item['quantity']
                product.price *= item['quantity']
                serializer_products.append(ProductShortSerializer(product).data)
            return Response(serializer_products, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        product = get_object_or_404(self.get_queryset_product(), id=request.data['id'])
        quantity = request.data['count']
        if request.user.is_authenticated:
            # Сохраняем продукт в корзину БД
            basket_item, created = BasketItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                basket_item.quantity += quantity
                basket_item.save()

        else:
            # Сохраняем продукт в сессию корзины
            basket = request.session.get('basket', [])
            for item in basket:
                if item['product'] == product.id:
                    item['quantity'] += quantity
                    break
            else:
                basket.append({
                    'product': product.id,
                    'quantity': quantity
                })

            request.session['basket'] = basket
        return self.get(request)

    def delete(self, request: Request) -> Response:
        product = get_object_or_404(self.get_queryset_product(), id=request.data['id'])
        quantity = request.data['count']
        if request.user.is_authenticated:
            # Удаляем продукт из корзины БД или изменяем его количество
            basket_item = get_object_or_404(BasketItem, user=request.user, product_id=product.id)
            if basket_item.quantity > quantity:
                basket_item.quantity -= quantity
                basket_item.save()
            else:
                basket_item.delete()
        else:
            # Удаляем продукт из сессии корзины или изменяем его количество
            basket = request.session.get('basket', [])
            for item in basket:
                if item['product'] == product.id:
                    if item['quantity'] > quantity:
                        item['quantity'] -= quantity
                    else:
                        basket.remove(item)
            request.session['basket'] = basket
        return self.get(request)


class OrdersAPIView(APIView):
    """
    Действия с заказами:
    - получить список активных заказов
    - создать заказ
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Order.objects.prefetch_related(
            Prefetch(
                'products__product',
                queryset=Product.objects.select_related('category').annotate(
                    reviews_count=Count('reviews'),
                    rating=Coalesce(Avg('reviews__rate'), Value(0.0))
                ).prefetch_related('images', 'tags')
            )
        ).order_by('-createdAt')

    def get(self, request: Request) -> Response:
        orders = self.get_queryset().filter(user=request.user, is_deleted=False)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            # Создаём заказ
            order = Order.objects.create()

            # Сохраняем orderId в сессии
            request.session['orderId'] = order.id

            # Корзина из сессии
            basket = request.session.get('basket', [])
            if basket:
                products_ids = [item['product'] for item in basket]
                products = {product.id: product for product in Product.objects.select_related('category'
                                                                                              ).prefetch_related(
                    'images', 'tags').annotate(rating=Coalesce(Avg('reviews__rate'), Value(0.00)),
                                               reviews_count=Count('reviews')).filter(id__in=products_ids)}
                order_products = []
                for basket_item in basket:
                    # Получаем продукт
                    product = products.get(basket_item['product'])

                    # Создаём OrderProduct
                    order_products.append(OrderProduct(
                        order=order,
                        product=product,
                        count=basket_item['quantity'],
                        price=float(product.price * basket_item['quantity'])))

                # Удаляем корзину из сессии
                del request.session['basket']

        else:
            # Создаём заказ
            order = Order.objects.create(
                user=request.user,
                fullName=request.user.fullName or request.user.first_name + request.user.last_name or request.user.username.title(),
                email=request.user.email or '',
                phone=request.user.phone or '',
            )

            # Получаем корзину из БД
            basket = BasketItem.objects.filter(user=request.user).prefetch_related(Prefetch(
                'product',
                queryset=Product.objects.select_related('category').annotate(
                    reviews_count=Count('reviews'),
                    rating=Coalesce(Avg('reviews__rate'), Value(0.0))
                ).prefetch_related('images', 'tags')
            ))

            # Создаём OrderProduct'ы
            order_products = [OrderProduct(
                order=order,
                product=basket_item.product,
                count=basket_item.quantity,
                price=float(basket_item.product.price * basket_item.quantity)
            ) for basket_item in basket
            ]

            # Очищаем корзину в БД
            basket.delete()

        OrderProduct.objects.bulk_create(order_products)

        # Определяем общую стоимость заказа
        order.totalCost = float(sum(product.price for product in order_products))
        order.save()

        return Response({'orderId': order.id}, status=status.HTTP_200_OK)


class OrderAPIView(APIView):
    """
    Действия с заказом:
    - получить заказ по ID
    - подтвердить заказ, меняя статус заказа с 'accepted' на 'confirmed'
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related(
            Prefetch(
                'products__product',
                queryset=Product.objects.select_related('category').annotate(
                    reviews_count=Count('reviews'),
                    rating=Coalesce(Avg('reviews__rate'), Value(0.0))
                ).prefetch_related('images', 'tags')
            )
        )

    def get(self, request: Request, pk) -> Response:
        order = get_object_or_404(self.get_queryset(), id=pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, pk) -> Response:
        order = get_object_or_404(self.get_queryset(), id=pk)

        # Обновляем данные заказа
        if request.data['fullName']:
            order.fullName = request.data['fullName']
        if request.data['phone']:
            order.phone = request.data['phone']
        if request.data['email']:
            order.email = request.data['email']
        if request.data['deliveryType']:
            order.deliveryType = request.data['deliveryType']
        if request.data['city']:
            order.city = request.data['city']
        if request.data['address']:
            order.address = request.data['address']
        if request.data['paymentType']:
            order.paymentType = request.data['paymentType']

        # Определяем общую стоимость заказа с учетом доставки
        delivery = get_object_or_404(DeliveryType)
        if request.data['deliveryType'] == 'ordinary':
            if order.totalCost < delivery.min_cost_order_by_free_delivery:
                order.totalCost += delivery.cost_ordinary_delivery
        elif request.data['deliveryType'] == 'express':
            order.totalCost += delivery.cost_express_delivery

        order.status = 'confirmed'
        order.save()

        return Response({'orderId': order.id}, status=status.HTTP_200_OK)


class PaymentAPIView(APIView):
    """Оплата заказа"""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk) -> Response:
        # Получаем заказ
        order = get_object_or_404(Order, id=pk, user=request.user)

        # Сериализуем данные и если они валидны, сохраняем в БД информацию по оплате заказа
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order)

            # Меняем статус заказа на "оплачен"
            order.status = 'paid'
            order.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
