from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


def avatar_directory_path(instance: 'User', filename: str) -> str:
    """Формирование пути для аватара"""
    return 'users/user_{pk}/avatar/{filename}'.format(
        pk=instance.pk,
        filename=filename,
    )


def validate_image_size(image):
    """Проверка размера изображения ≤ 2 МБ"""
    max_size_mb = 2
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'Размер аватарки не должен превышать {max_size_mb} МБ.')


class User(AbstractUser):
    """Кастомная модель пользователя с расширенными полями"""
    fullName = models.CharField(max_length=300, blank=False)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(
        blank=True,
        null=True,
        upload_to=avatar_directory_path,
        validators=[validate_image_size],
    )
