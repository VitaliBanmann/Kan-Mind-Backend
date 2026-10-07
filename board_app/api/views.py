from django.db.models import Q
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Board
from .permissions import IsBoardMemberOrOwner, IsBoardOwner
from .serializers import (
    BoardDetailSerializer,
    BoardPatchResponseSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
)


class BoardViewSet(viewsets.ModelViewSet):
    """Handle standard board CRUD with board-specific response shapes."""

    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'board_id'

    def get_queryset(self):
        """Limit board lists to boards accessible to the current user."""
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(
                Q(owner=self.request.user) | Q(members=self.request.user)
            ).distinct()
        return queryset

    def get_serializer_class(self):
        """Use the response serializer appropriate to each board action."""
        if self.action == 'retrieve':
            return BoardDetailSerializer
        if self.action in ('update', 'partial_update'):
            return BoardUpdateSerializer
        return BoardSerializer

    def get_permissions(self):
        """Apply object permissions to board detail operations."""
        if self.action == 'destroy':
            return [IsAuthenticated(), IsBoardOwner()]
        if self.action in ('retrieve', 'update', 'partial_update'):
            return [IsAuthenticated(), IsBoardMemberOrOwner()]
        return super().get_permissions()

    def get_object(self):
        """Keep the API's established not-found response message."""
        try:
            return super().get_object()
        except Http404 as error:
            raise NotFound('Board not found') from error

    def perform_create(self, serializer):
        """Assign the authenticated user as owner and board member."""
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)

    def update(self, request, *args, **kwargs):
        """Update a board and return the documented patch response shape."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        response_serializer = BoardPatchResponseSerializer(
            serializer.instance
        )
        return Response(response_serializer.data)
