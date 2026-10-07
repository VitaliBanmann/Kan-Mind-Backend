from django.test import TestCase


from auth_app.models import User
from board_app.models import Board
from task_app.models import Task
from task_app.api.permissions import IsBoardMember


class IsBoardMemberTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='password123',
            fullname='Board Owner',
        )

        self.member = User.objects.create_user(
            email='member@test.com',
            password='password123',
            fullname='Board Member',
        )

        self.outsider = User.objects.create_user(
            email='outsider@test.com',
            password='password123',
            fullname='Outsider',
        )

        self.board = Board.objects.create(
            title='Test Board',
            owner=self.owner,
        )

        self.board.members.add(
            self.owner,
            self.member,
        )

        self.task = Task.objects.create(
            board=self.board,
            title='Test Task',
            description='Test Description',
            status='to-do',
            priority='medium',
            assignee=self.member,
            reviewer=self.member,
            creator=self.owner,
        )

    def test_board_member_has_permission(self):
        permission = IsBoardMember()

        request = type(
            'Request',
            (),
            {
                'data': {'board': self.board.id},
                'user': self.member,
            },
        )()

        view = type('View', (), {'kwargs': {}})()

        self.assertTrue(
            permission.has_permission(request, view)
        )

    def test_non_member_has_no_permission(self):
        permission = IsBoardMember()

        request = type(
            'Request',
            (),
            {
                'data': {'board': self.board.id},
                'user': self.outsider,
            },
        )()

        view = type('View', (), {'kwargs': {}})()

        self.assertFalse(
            permission.has_permission(request, view)
        )

    def test_board_member_has_task_permission(self):
        permission = IsBoardMember()

        request = type(
            'Request',
            (),
            {
                'data': {},
                'user': self.member,
            },
        )()

        view = type(
            'View',
            (),
            {
                'kwargs': {'task_id': self.task.id},
            },
        )()

        self.assertTrue(
            permission.has_permission(request, view)
        )

    def test_non_member_has_no_task_permission(self):
        permission = IsBoardMember()

        request = type(
            'Request',
            (),
            {
                'data': {},
                'user': self.outsider,
            },
        )()

        view = type(
            'View',
            (),
            {
                'kwargs': {'task_id': self.task.id},
            },
        )()

        self.assertFalse(
            permission.has_permission(request, view)
        )

    def test_missing_board_defers_to_serializer_validation(self):
        permission = IsBoardMember()

        request = type(
            'Request',
            (),
            {
                'data': {},
                'user': self.member,
            },
        )()

        view = type('View', (), {'kwargs': {}})()

        self.assertTrue(
            permission.has_permission(request, view)
        )
