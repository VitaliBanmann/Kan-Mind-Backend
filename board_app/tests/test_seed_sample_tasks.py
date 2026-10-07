from io import StringIO

from django.core.management import call_command, CommandError
from django.test import TestCase

from auth_app.models import User
from board_app.models import Board
from task_app.models import Task


class SeedSampleTasksCommandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='seed-user@test.com',
            password='password123',
            fullname='Seed User',
        )

    def test_command_requires_an_existing_user(self):
        with self.assertRaises(CommandError):
            call_command('seed_sample_tasks', email='missing@test.com')

        self.assertFalse(Board.objects.exists())

    def test_command_creates_samples_and_is_idempotent(self):
        output = StringIO()

        call_command(
            'seed_sample_tasks',
            email=self.user.email,
            board_title='Test Sample Board',
            stdout=output,
        )

        board = Board.objects.get(
            title='Test Sample Board',
            owner=self.user,
        )
        self.assertIn(self.user, board.members.all())
        self.assertEqual(Task.objects.filter(board=board).count(), 5)
        self.assertIn('created 5 new sample tasks', output.getvalue())

        output = StringIO()
        call_command(
            'seed_sample_tasks',
            email=self.user.email,
            board_title='Test Sample Board',
            stdout=output,
        )

        self.assertEqual(Task.objects.filter(board=board).count(), 5)
        self.assertIn(
            'already existed; created 0 new sample tasks',
            output.getvalue(),
        )
