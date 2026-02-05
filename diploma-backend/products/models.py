from django.db import models


def category_image_directory_path(instance: 'Category', filename: str) -> str:
    """Определяем путь к каталогу изображений категории продукта"""
    return 'products/category_{pk}/images/{filename}'.format(
        pk=instance.pk,
        filename=filename,
    )


class Category(models.Model):
    """Модель Category представляет собой категорию товаров"""
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=category_image_directory_path, null=True, blank=True)
    parent = models.ForeignKey(
            'self',
            on_delete=models.CASCADE,
            null=True,
            blank=True,
            related_name='subcategories'
        )
    is_deleted = models.BooleanField(default=False, db_index=True)   # для мягкого удаления

    class Meta:
        verbose_name_plural = "Categories"                           # множественное число названия модели

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Модель Tag представляет собой тег"""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель Product представляет собой товар"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=150, db_index=True)
    description = models.TextField(null=False, blank=True)
    fullDescription = models.TextField(null=False, blank=True)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2, db_index=True)
    count = models.PositiveIntegerField(default=0, db_index=True)
    freeDelivery = models.BooleanField(default=False, db_index=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    is_deleted = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.title


def product_image_directory_path(instance: 'ProductImage', filename: str) -> str:
    """Определяем путь к каталогу изображений продукта"""
    return 'products/product_{pk}/images/{filename}'.format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    """Модель ProductImage представляет собой изображение продукта"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    src = models.ImageField(upload_to=product_image_directory_path)
    alt = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'Image {self.product.title}'


class Specification(models.Model):
    """Модель Specification описывает характеристики продукта"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=200)

    def __str__(self):
        return f'Specification {self.product.title}'


class Review(models.Model):
    """Модель Review представляет собой отзыв на продукт"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    author = models.CharField(max_length=200)
    email = models.EmailField()
    text = models.TextField()
    rate = models.PositiveSmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review {self.author} on {self.product.title}'


class Sale(models.Model):
    """Модель Sale представляет собой скидку на продукт"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='sale')
    salePrice = models.DecimalField(max_digits=10, decimal_places=2)
    dateFrom = models.DateField()
    dateTo = models.DateField()

    def __str__(self):
        return f'Sale on {self.product.title}'
