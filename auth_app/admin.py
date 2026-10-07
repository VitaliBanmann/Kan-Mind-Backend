from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'fullname', 'is_staff', 'is_active')
    search_fields = ('email', 'fullname')
    ordering = ('email',)
