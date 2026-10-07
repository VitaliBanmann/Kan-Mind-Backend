from django.test import TestCase

from auth_app.models import User
from board_app.models import Board
from task_app.models import Task
from task_app.api.serializers import (
    TaskCreateSerializer,
    TaskUpdateSerializer,
)


class TaskCreateSerializerTest(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='password123',
            fullname="Board Owner",
        )

        self.member = User.objects.create_user(
            email="member@test.com",
            password="password123",
            fullname="Board Member",
        )

        self.board = Board.objects.create(
            title="Test Board",
            owner=self.owner,
        )

        self.board.members.add(self.owner, self.member)

    def test_create_task_with_valid_data(self):
        data = {
            'board': self.board.id,
            'title': 'Test Task',
            'description': 'Test Description',
            'status': 'to-do',
            'priority': 'high',
            'assignee_id': self.member.id,
            'reviewer_id': self.member.id,
            'due_date': '2026-08-20'
        }

        serializer = TaskCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_reject_assignee_not_in_board(self):
        outsider = User.objects.create_user(
            email='outsider@test.com',
            password='password123',
            fullname='Outsider',
        )

        data = {
            'board': self.board.id,
            'title': 'Invalid Task',
            'description': 'Invalid Description',
            'status': 'to-do',
            'priority': 'high',
            'assignee_id': outsider.id,
            'reviewer_id': self.member.id,
            'due_date': '2026-08-20',
        }

        serializer = TaskCreateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('assignee_id', serializer.errors)

    def test_reject_reviewer_not_in_board(self):
        outsider = User.objects.create_user(
            email='reviewer-outsider@test.com',
            password='password123',
            fullname='Reviewer Outsider',
        )

        data = {
            'board': self.board.id,
            'title': 'Invalid Reviewer Task',
            'description': 'Invalid Description',
            'status': 'to-do',
            'priority': 'medium',
            'assignee_id': self.member.id,
            'reviewer_id': outsider.id,
            'due_date': '2026-08-20',
        }

        serializer = TaskCreateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('reviewer_id', serializer.errors)

    def test_update_rejects_assignee_not_in_board(self):
        task = Task.objects.create(
            board=self.board,
            title='Test Task',
            description='Test Description',
            status='to-do',
            priority='medium',
            assignee=self.member,
            reviewer=self.member,
            creator=self.owner,
        )

        outsider = User.objects.create_user(
            email='update-outsider@test.com',
            password='password123',
            fullname='Update Outsider',
        )

        data = {
            'assignee_id': outsider.id,
        }

        serializer = TaskUpdateSerializer(
            task,
            data=data,
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('assignee_id', serializer.errors)

    def test_update_rejects_reviewer_not_in_board(self):
        task = Task.objects.create(
            board=self.board,
            title='Test Task',
            description='Test Description',
            status='to-do',
            priority='medium',
            assignee=self.member,
            reviewer=self.member,
            creator=self.owner,
        )

        outsider = User.objects.create_user(
            email='reviewer-update-outsider@test.com',
            password='password123',
            fullname='Reviewer Outsider',
        )

        data = {
            'reviewer_id': outsider.id,
        }

        serializer = TaskUpdateSerializer(
            task,
            data=data,
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('reviewer_id', serializer.errors)
