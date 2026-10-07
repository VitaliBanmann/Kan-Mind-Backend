from rest_framework import serializers


from ..models import Board
from auth_app.models import User
from auth_app.api.serializers import UserSerializer
from task_app.api.serializers import TaskDetailSerializer


class BoardSerializer(serializers.ModelSerializer):
    """Serialize board data with member and task statistics."""

    owner_id = serializers.IntegerField(
        source="owner.id",
        read_only=True,
    )
    member_count = serializers.IntegerField(
        source="members.count",
        read_only=True,
    )
    ticket_count = serializers.IntegerField(
        source="tasks.count",
        read_only=True,
    )

    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with to-do status."""
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of tasks with high priority."""
        return obj.tasks.filter(priority="high").count()

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serialize detailed board data including members and tasks."""

    owner_id = serializers.IntegerField(
        source='owner.id',
        read_only=True,
    )
    members = UserSerializer(
        many=True,
        read_only=True,
    )
    tasks = TaskDetailSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks',
        ]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Validate data used to update a board."""
    class Meta:

        model = Board
        fields = [
            'title',
            'members',
        ]


class BoardPatchResponseSerializer(serializers.ModelSerializer):
    """A serializer for the patch Response"""
    owner_data = UserSerializer(
        source="owner",
        read_only=True,
    )

    members_data = UserSerializer(
        source="members",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_data",
            "members_data",
        ]
