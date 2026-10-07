from django.contrib import admin

from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Configure the Django admin interface for boards."""

    list_display = ('title', 'owner')
    search_fields = ('title', 'owner__email')
