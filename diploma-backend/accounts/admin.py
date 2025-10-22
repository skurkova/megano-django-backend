from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = 'pk', 'username', 'fullName', 'phone', 'email'
    search_fields = 'fullName', 'phone', 'email'
    ordering = 'pk',
    list_display_links = 'pk', 'username'

    # Для редактирования существующего пользователя
    fieldsets = UserAdmin.fieldsets + (
        ('Additional info', {'fields': ('phone', 'avatar')}),
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
