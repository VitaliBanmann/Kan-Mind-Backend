from django.test import TestCase

from auth_app.models import User
from board_app.models import Board
from task_app.models import Comment, Task


class TaskModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='task-model@test.com',
            password='password123',
            fullname='Task Model User',
        )

        self.board = Board.objects.create(
            title='Task Board',
            owner=self.user,
        )

    def test_task_str_returns_title(self):
        task = Task.objects.create(
            board=self.board,
            title='My Test Task',
            creator=self.user,
        )

        self.assertEqual(
            str(task),
            'My Test Task',
        )

    def test_comment_str_returns_author_and_task(self):
        task = Task.objects.create(
            board=self.board,
            title='My Test Task',
            creator=self.user,
        )

        comment = Comment.objects.create(
            task=task,
            author=self.user,
            content='Test comment',
        )

        self.assertEqual(
            str(comment),
            'comment by task-model@test.com on My Test Task',
        )
