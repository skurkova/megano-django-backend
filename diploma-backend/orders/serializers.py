from rest_framework import serializers

from .models import BasketItem, Order, OrderProduct, Payment, DeliveryType

from products.serializers import ImageSerializer, TagSerializer, ProductShortSerializer


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор общей информации о продукте в заказе
    """
    id = serializers.IntegerField(source='product.id')
    category = serializers.IntegerField(source='product.category_id')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    count = serializers.IntegerField()
    date = serializers.DateTimeField(source='product.date')
    title = serializers.CharField(source='product.title')
    description = serializers.CharField(source='product.description')
    freeDelivery = serializers.BooleanField(source='product.freeDelivery')
    images = ImageSerializer(source='product.images', many=True)
    tags = TagSerializer(source='product.tags', many=True)
    reviews = serializers.IntegerField(source='product.reviews_count')
    rating = serializers.DecimalField(source='product.rating', max_digits=3, decimal_places=2)

    class Meta:
        model = OrderProduct
        fields = (
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'rating'
        )


class BasketItemSerializer(serializers.ModelSerializer):
    """Сериализатор элемента корзины"""
    product = ProductShortSerializer()
    count = serializers.IntegerField(source='quantity')

    class Meta:
        model = BasketItem
        fields = (
            'product',
            'count',
        )


class BasketItemResponseSerializer(serializers.ModelSerializer):
    """
    Сериализатор ответа для корзины с общей информацией о продукте
    """
    id = serializers.IntegerField(source='product.id')
    category = serializers.IntegerField(source='product.category_id')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    count = serializers.IntegerField(source='quantity')
    date = serializers.DateTimeField(source='product.date')
    title = serializers.CharField(source='product.title')
    description = serializers.CharField(source='product.description')
    freeDelivery = serializers.BooleanField(source='product.freeDelivery')
    images = ImageSerializer(source='product.images', many=True)
    tags = TagSerializer(source='product.tags', many=True)
    reviews = serializers.IntegerField(source='product.reviews_count')
    rating = serializers.DecimalField(source='product.rating', max_digits=3, decimal_places=2)

    class Meta:
        model = BasketItem
        fields = (
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'rating'
        )


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор заказа"""
    products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'createdAt',
            'fullName',
            'email',
            'phone',
            'deliveryType',
            'paymentType',
            'totalCost',
            'status',
            'city',
            'address',
            'products'
        )


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор оплаты заказа"""

    class Meta:
        model = Payment
        fields = (
            'number',
            'name',
            'month',
            'year',
            'code'
        )

    def validate_number(self, value):
        """Проверка валидности номера карты"""
        if not value.isdigit():
            raise serializers.ValidationError('The number must contain only numbers')
        if len(str(value)) > 8:
            raise serializers.ValidationError('The number must not be longer than 8 digits')
        if value.endswith('0'):
            raise serializers.ValidationError('The number must not end with zero')
        if int(value) % 2 != 0:
            raise serializers.ValidationError('The number must be even')
        return value

    def validate_month(self, value):
        """Проверка валидности цифр, обозначающих месяц"""
        if not value.isdigit():
            raise serializers.ValidationError('The month must contain only numbers')
        if len(str(value)) != 2:
            raise serializers.ValidationError('The month must not be longer than 2 digits')
        if 12 < int(value) < 1:
            raise serializers.ValidationError('The month must be of 1 do 12 number')
        return value

    def validate_year(self, value):
        """Проверка валидности цифр, обозначающих год"""
        if not value.isdigit():
            raise serializers.ValidationError('The year must contain only numbers')
        if len(str(value)) != 4:
            raise serializers.ValidationError('The year must be 4 digits')
        return value

    def validate_code(self, value):
        """Проверка валидности трехзначного кода"""
        if not value.isdigit():
            raise serializers.ValidationError('The code must contain only numbers')
        if len(str(value)) != 3:
            raise serializers.ValidationError('The code must be 3 digits')
        return value
