from django.test import TestCase

from auth_app.models import User
from board_app.models import Board


class BoardModelTest(TestCase):

    def test_board_str_returns_title(self):
        user=User.objects.create_user(
            email='board-model@test.com',
            password='password123',
            fullname='Board Model User',
        )

        board=Board.objects.create(
            title='My Test Board',
            owner=user,
        )

        self.assertEqual(
            str(board),
            'My Test Board',
        )

    def test_board_owner_is_saved_correctly(self):
        user = User.objects.create_user(
            email='owner@test.com',
            password='password123',
            fullname='Board Owner',
        )

        board = Board.objects.create(
            title='Owner Test Board',
            owner=user,
        )

        self.assertEqual(
            board.owner,
            user,
        )

    def test_board_members_can_be_added(self):
        owner = User.objects.create_user(
            email='owner@test.com',
            password='password123',
            fullname='Board Owner',
        )

        member = User.objects.create_user(
            email='member@test.com',
            password='password123',
            fullname='Board Member',
        )

        board = Board.objects.create(
            title='Member Test Board',
            owner=owner,
        )

        board.members.add(member)

        self.assertIn(
            member,
            board.members.all(),
        )

    def test_board_can_have_multiple_members(self):
        owner = User.objects.create_user(
            email='owner@test.com',
            password='password123',
            fullname='Board Owner',
        )

        member_one = User.objects.create_user(
            email='member1@test.com',
            password='password123',
            fullname='Member One',
        )

        member_two = User.objects.create_user(
            email='member2@test.com',
            password='password123',
            fullname='Member Two',
        )

        board = Board.objects.create(
            title='Multiple Members Board',
            owner=owner,
        )

        board.members.add(member_one, member_two)

        self.assertEqual(
            board.members.count(),
            2,
        )