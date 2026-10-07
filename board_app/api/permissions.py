from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):
    """Allow access to a board for its owner or one of its members."""

    message = "Permission denied"

    def has_object_permission(self, request, view, board):
        """Check whether the current user can access the board."""
        return (
            board.owner_id == request.user.id
            or board.members.filter(id=request.user.id).exists()
        )


class IsBoardOwner(BasePermission):
    """Allow destructive board actions only to the board owner."""

    message = "Permission denied"

    def has_object_permission(self, request, view, board):
        """Check whether the current user owns the board."""
        return board.owner_id == request.user.id
