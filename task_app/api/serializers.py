from rest_framework import serializers

from auth_app.models import User
from ..models import Task, Comment
from auth_app.api.serializers import UserSerializer


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serialize task details including assigned users and comment count."""

    assignee = UserSerializer(read_only=True)
    board = serializers.IntegerField(
        source="board_id",
        read_only=True,
    )
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.IntegerField(
        source='comments.count',
        read_only=True,
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count',
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """Validate and serialize data for creating a task."""

    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        """Ensure assignee and reviewer belong to the selected board."""
        board = attrs['board']
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')

        if assignee and not board.members.filter(id=assignee.id).exists():
            raise serializers.ValidationError(
                {"assignee_id": "User is not a member of this board."}
            )

        if reviewer and not board.members.filter(id=reviewer.id).exists():
            raise serializers.ValidationError(
                {"reviewer_id": "User is not a member of this board."}
            )

        return attrs

    class Meta:
        model = Task
        fields = [
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee_id',
            'reviewer_id',
            'due_date',
        ]


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Validate and serialize data for updating a task."""

    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        """Ensure assignee and reviewer belong to the task's board."""
        board = self.instance.board
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')

        if assignee and not board.members.filter(id=assignee.id).exists():
            raise serializers.ValidationError(
                {"assignee_id": "User is not a member of this board."}
            )

        if reviewer and not board.members.filter(id=reviewer.id).exists():
            raise serializers.ValidationError(
                {"reviewer_id": "User is not a member of this board."}
            )

        return attrs

    class Meta:
        model = Task
        fields = [
            'title',
            'status',
            'description',
            'priority',
            'assignee_id',
            'reviewer_id',
            'due_date',
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Serialize comments together with their task and author."""
    author = serializers.CharField(
        source="author.fullname",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = [
            'id',
            'created_at',
            'author',
            'content',
        ]
