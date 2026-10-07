from django.urls import path

from .views import (
    AssignedTasksView,
    TaskViewSet,
    ReviewingTasksView,
    CommentsView,
)


urlpatterns = [
    path(
        'tasks/',
        TaskViewSet.as_view({'post': 'create'}),
        name="task-list",
    ),
    path(
        'tasks/assigned-to-me/',
        AssignedTasksView.as_view(),
        name="assigned-tasks",
    ),
    path(
        'tasks/reviewing/',
        ReviewingTasksView.as_view(),
        name="reviewing-tasks",
    ),
    path(
        'tasks/<int:task_id>/',
        TaskViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name="task-detail",
    ),
    path(
        'tasks/<int:task_id>/comments/',
        CommentsView.as_view(),
        name="task-comments",
    ),
    path(
        'tasks/<int:task_id>/comments/<int:comment_id>/',
        CommentsView.as_view(),
        name="comment-detail",
    ),
]
