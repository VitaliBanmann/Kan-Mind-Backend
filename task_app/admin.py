from django.contrib import admin

from .models import Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Configure the Django admin interface for tasks."""

    list_display = (
        'title',
        'board',
        'status',
        'priority',
        'assignee',
        'reviewer',
        'due_date',
    )
    search_fields = ('title', 'description')
    list_filter = ('status', 'priority')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Configure the Django admin interface for comments."""

    list_display = ('task', 'author', 'created_at')
    search_fields = ('content', 'author__email')
    ordering = ('-created_at',)
