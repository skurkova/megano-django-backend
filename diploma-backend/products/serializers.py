from rest_framework import serializers

from .models import Tag, Category, ProductImage, Product, Specification, Sale, Review


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name'
        )


class ImageSerializer(serializers.ModelSerializer):
    """Сериализатор картинок"""

    class Meta:
        model = ProductImage
        fields = ('src', 'alt')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий"""
    subcategories = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id',
            'title',
            'image',
            'subcategories',
        )

    def get_subcategories(self, obj):
        """Получаем подкатегории"""
        # Получаем только неудалённые подкатегории
        subcategories = obj.subcategories.filter(is_deleted=False)
        return CategorySerializer(subcategories, many=True, context=self.context).data

    def get_image(self, obj):
        return {
            "src": obj.image.url,
            "alt": obj.title}


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов"""

    class Meta:
        model = Review
        fields = (
            'id',
            'author',
            'email',
            'text',
            'rate',
            'date',
        )


class ProductShortSerializer(serializers.ModelSerializer):
    """Сериализатор общей информации о продуктах"""
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)
    reviews = serializers.IntegerField(source='reviews_count')
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    class Meta:
        model = Product
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


class SpecificationSerializer(serializers.ModelSerializer):
    """Сериализатор спецификаций"""

    class Meta:
        model = Specification
        fields = (
            'id',
            'name',
            'value',
        )


class ProductFullSerializer(serializers.ModelSerializer):
    """Сериализатор подробной информации о продуктах"""
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    specifications = SpecificationSerializer(many=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    class Meta:
        model = Product
        fields = (
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'fullDescription',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'specifications',
            'rating',
        )


class SaleSerializer(serializers.ModelSerializer):
    """Сериализатор скидок"""
    price = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    dateFrom = serializers.SerializerMethodField()
    dateTo = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = (
            'id',
            'price',
            'salePrice',
            'dateFrom',
            'dateTo',
            'title',
            'images',
        )

    def get_price(self, obj):
        return obj.product.price

    def get_title(self, obj):
        return obj.product.title

    def get_dateFrom(self, obj):
        return obj.dateFrom.strftime('%m-%d')

    def get_dateTo(self, obj):
        return obj.dateTo.strftime('%m-%d')

    def get_images(self, obj):
        return ImageSerializer(obj.product.images.all(), many=True).data
