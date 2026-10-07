from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Task, Comment
from .permissions import IsBoardMember, IsTaskCreatorOrBoardOwner
from .serializers import (
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    CommentSerializer,
)


class AssignedTasksView(APIView):
    """Provide tasks assigned to the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all tasks assigned to the current user."""
        tasks = Task.objects.filter(assignee=request.user)
        serializer = TaskDetailSerializer(tasks, many=True)
        return Response(serializer.data)


class ReviewingTasksView(APIView):
    """Provide tasks that the authenticated user has to review."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all tasks assigned to the current user for review."""
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = TaskDetailSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """Handle standard task CRUD while preserving API response shapes."""

    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    lookup_url_kwarg = 'task_id'

    def get_serializer_class(self):
        """Use input serializers for create and update actions."""
        if self.action == 'create':
            return TaskCreateSerializer
        if self.action in ('update', 'partial_update'):
            return TaskUpdateSerializer
        return TaskDetailSerializer

    def get_permissions(self):
        """Require the task creator or board owner to delete a task."""
        if self.action == 'destroy':
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return super().get_permissions()

    def get_object(self):
        """Keep the API's established not-found response message."""
        try:
            return super().get_object()
        except Http404 as error:
            raise NotFound('Task not found.') from error

    def create(self, request, *args, **kwargs):
        """Create a task and return its detailed representation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            TaskDetailSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        """Record the authenticated user as the task creator."""
        serializer.save(creator=self.request.user)

    def update(self, request, *args, **kwargs):
        """Return task details after a successful partial update."""
        response = super().update(request, *args, **kwargs)
        return Response(
            TaskDetailSerializer(self.get_object()).data,
            status=response.status_code,
            headers=response.headers,
        )


class CommentsView(APIView):
    """Handle comments belonging to a specific task."""

    permission_classes = [IsAuthenticated, IsBoardMember]

    def get(self, request, task_id):
        """Return all comments belonging to the requested task."""
        task = self._get_task(task_id)

        if task is None:
            return self._not_found()

        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        """Create a new comment for the requested task."""
        task = self._get_task(task_id)

        if task is None:
            return self._not_found()

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            return self._create_comment(serializer, task, request.user)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, task_id, comment_id):
        """Delete a comment if the authenticated user is its author."""
        comment = Comment.objects.filter(
            id=comment_id,
            task_id=task_id,
        ).first()

        if comment is None:
            return Response(
                {"detail": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if comment.author != request.user:
            return Response(
                {"detail": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_task(self, task_id):
        """Return the task with the given ID or None if it does not exist."""
        return Task.objects.filter(id=task_id).first()

    def _not_found(self):
        """Return the standard response for a missing task."""
        return Response(
            {"detail": "Task not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def _create_comment(self, serializer, task, user):
        """Save and return a new comment for the specified task."""
        comment = serializer.save(task=task, author=user)
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )
