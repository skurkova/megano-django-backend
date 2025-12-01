import json

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import validate_image_size
from .serializers import UserSerializer, SignUpSerializer, SignInSerializer, ChangePasswordSerializer

from orders.models import Order


class SignUpView(APIView):
    """Регистрация пользователя"""
    def post(self, request: Request):
        # Распарсим request.body как JSON
        body = request.body.decode('utf-8')
        data = json.loads(body)

        serializer = SignUpSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()

        # Логинимся
        login(request, user)

        # Привязываем пользователя к заказу, если он есть в сессии
        order_id = request.session.get('orderId')
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            order.user = user
            order.fullName = user.fullName or user.first_name + user.last_name or user.username.title()
            order.save()
            del request.session['orderId']

        return Response({'message': 'Successfully signed in'}, status=status.HTTP_200_OK)


class SignInView(APIView):
    """Авторизация пользователя"""
    def post(self, request: Request):
        # Распарсим request.body как JSON
        body = request.body.decode('utf-8')
        data = json.loads(body)

        serializer = SignInSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Проверяем, существует ли пользователь с таким username и password
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Логинимся
        login(request, user)

        # Привязываем пользователя к заказу, если он есть в сессии
        order_id = request.session.get('orderId')
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            order.user = user
            order.fullName = user.fullName or user.first_name + user.last_name or user.username.title()
            order.save()
            del request.session['orderId']

        return Response({'message': 'Successfully signed in'}, status=status.HTTP_200_OK)


class SignOutView(APIView):
    """Выход авторизированного пользователя"""
    def post(self, request: Request):
        if request.user.is_authenticated:
            logout(request)
            return Response({'message': 'Successfully signed out'}, status=status.HTTP_200_OK)


class ProfileUserView(APIView):
    """Просмотр профиля пользователя"""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = UserSerializer(instance=request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AvatarUploadView(APIView):
    """Загрузка аватара пользователя"""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        avatar = request.FILES.get('avatar')
        if not avatar:
            return Response({'avatar': 'Not found file'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_image_size(avatar)
        except ValidationError as exp:
            return Response({'avatar': exp.messages}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        request.user.avatar = avatar
        user.save()
        return Response({'avatar': 'Successful update user avatar'}, status=status.HTTP_200_OK)


class ChangeUserPasswordView(APIView):
    """Обновить пароль пользователя"""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = ChangePasswordSerializer(instance=request.user, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        # Обновляем сессию, чтобы не разлогиниться
        update_session_auth_hash(request, request.user)
        return Response({'newPassword': 'New password successfully changed.'}, status=status.HTTP_200_OK)

