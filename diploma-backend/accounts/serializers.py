from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import User


class SignUpSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=300, required=True)
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('User with login already exists')
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exp:
            raise serializers.ValidationError(exp.messages)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            fullName=validated_data['name'],
            password=validated_data['password'],
        )
        return user


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('fullName', 'email', 'phone', 'avatar')
        extra_kwargs = {
            'fullName': {'required': True},
            'email': {'required': True},
        }

    def validate_email(self, value):
        """Проверка валидности и уникальности email"""
        try:
            validate_email(value)
        except ValidationError as exp:
            raise serializers.ValidationError(exp.messages)

        if User.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError('User with this email already exists')
        return value

    def validate_phone(self, value):
        """Проверка валидности и уникальности phone"""
        if value:
            check_value = value[1:] if value.startswith('+') else value
            if not check_value.isdigit():
                raise serializers.ValidationError('Phone must contain only numbers')

            if User.objects.filter(phone=value).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise serializers.ValidationError('User with this phone already exists.')
        return value

    def update(self, instance, validated_data):
        """Обновляем данные пользователя"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(required=True, write_only=True)
    newPassword = serializers.CharField(required=True, write_only=True)

    def validate_currentPassword(self, value):
        user = self.instance
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is entered incorrectly')
        return value

    def validate_newPassword(self, value):
        user = self.instance
        if user.check_password(value):
            raise serializers.ValidationError('New password cannot match current password.')
        try:
            validate_password(value)
        except ValidationError as exp:
            raise serializers.ValidationError(exp.messages)
        return value

    def update(self, instance, validated_data):
        """Обновляем пароль пользователя"""
        instance.set_password(validated_data['newPassword'])
        instance.save()
        return instance
