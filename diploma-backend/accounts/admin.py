from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.action(description='Mark deleted')
def soft_delete(modeladmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(is_deleted=True)


@admin.action(description='Restore')
def restore(modeladmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(is_deleted=False)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = 'pk', 'username', 'fullName', 'phone', 'email', 'is_deleted'
    list_display_links = 'pk', 'username'
    search_fields = 'username', 'fullName', 'phone', 'email'
    ordering = 'pk',
    actions = [soft_delete, restore]

    # Для редактирования существующего пользователя
    fieldsets = UserAdmin.fieldsets + (
        ('Additional info', {'fields': ('fullName', 'phone', 'avatar', 'is_deleted')}),
    )

    # Для создания нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal info', {
            'fields': ('fullName', 'email'),
        }),
        ('Additional info', {'fields': ('phone', 'avatar')}),
    )
