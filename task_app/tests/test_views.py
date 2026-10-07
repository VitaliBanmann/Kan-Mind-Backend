from django.test import TestCase
from rest_framework.test import APIClient

from auth_app.models import User
from board_app.models import Board
from task_app.models import Task, Comment


class TaskViewsTest(TestCase):

    def setUp(self):
        self.client = APIClient()

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
            creator=self.owner,
            assignee=self.member,
            reviewer=self.member,
        )

    def test_assigned_tasks_requires_authentication(self):
        response = self.client.get(
            '/api/tasks/assigned-to-me/'
        )

        self.assertEqual(response.status_code, 401)

    def test_assigned_tasks_returns_user_tasks(self):
        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.get(
            '/api/tasks/assigned-to-me/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['id'],
            self.task.id,
        )

    def test_assigned_tasks_excludes_other_users_tasks(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.get(
            '/api/tasks/assigned-to-me/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_reviewing_tasks_requires_authentication(self):
        response = self.client.get(
            '/api/tasks/reviewing/'
        )

        self.assertEqual(response.status_code, 401)

    def test_reviewing_tasks_returns_user_tasks(self):
        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.get(
            '/api/tasks/reviewing/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['id'],
            self.task.id,
        )

    def test_reviewing_tasks_excludes_other_users_tasks(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.get(
            '/api/tasks/reviewing/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_create_task_requires_authentication(self):
        data = {
            'board': self.board.id,
            'title': 'New Task',
            'description': 'New Description',
            'status': 'to-do',
            'priority': 'medium',
            'assignee_id': self.member.id,
            'reviewer_id': self.member.id,
            'due_date': '2026-08-20',
        }

        response = self.client.post(
            '/api/tasks/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_create_task_without_board_returns_bad_request(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(
            '/api/tasks/',
            {
                'title': 'Task without board',
                'description': 'A board is required.',
                'status': 'to-do',
                'priority': 'medium',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_create_task_with_invalid_board_returns_bad_request(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(
            '/api/tasks/',
            {
                'board': 'not-a-board-id',
                'title': 'Task with invalid board',
                'description': 'The board ID must be an integer.',
                'status': 'to-do',
                'priority': 'medium',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('board', response.data)

    def test_create_task_with_unknown_board_returns_not_found(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(
            '/api/tasks/',
            {
                'board': 99999,
                'title': 'Task with unknown board',
                'description': 'The board does not exist.',
                'status': 'to-do',
                'priority': 'medium',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 404)

    def test_create_task_as_board_member(self):
        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'board': self.board.id,
            'title': 'Created Task',
            'description': 'Created through API',
            'status': 'to-do',
            'priority': 'high',
            'assignee_id': self.member.id,
            'reviewer_id': self.member.id,
            'due_date': '2026-08-20',
        }

        response = self.client.post(
            '/api/tasks/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data['title'],
            'Created Task',
        )
        self.assertEqual(
            response.data['assignee']['id'],
            self.member.id,
        )
        self.assertEqual(
            response.data['reviewer']['id'],
            self.member.id,
        )

    def test_create_task_as_non_member_forbidden(self):
        self.client.force_authenticate(
            user=self.outsider
        )

        data = {
            'board': self.board.id,
            'title': 'Forbidden Task',
            'description': 'Should not be created',
            'status': 'to-do',
            'priority': 'medium',
            'assignee_id': self.member.id,
            'reviewer_id': self.member.id,
            'due_date': '2026-08-20',
        }

        response = self.client.post(
            '/api/tasks/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_create_task_rejects_assignee_not_in_board(self):
        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'board': self.board.id,
            'title': 'Invalid Assignee Task',
            'description': 'Should be rejected',
            'status': 'to-do',
            'priority': 'medium',
            'assignee_id': self.outsider.id,
            'reviewer_id': self.member.id,
            'due_date': '2026-08-20',
        }

        response = self.client.post(
            '/api/tasks/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'assignee_id',
            response.data,
        )

    def test_create_task_rejects_reviewer_not_in_board(self):
        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'board': self.board.id,
            'title': 'Invalid Reviewer Task',
            'description': 'Should be rejected',
            'status': 'to-do',
            'priority': 'medium',
            'assignee_id': self.member.id,
            'reviewer_id': self.outsider.id,
            'due_date': '2026-08-20',
        }

        response = self.client.post(
            '/api/tasks/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'reviewer_id',
            response.data,
        )

    def test_get_task_requires_authentication(self):
        response = self.client.get(
            f'/api/tasks/{self.task.id}/'
        )

        self.assertEqual(response.status_code, 401)

    def test_get_task_as_board_member(self):
        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.get(
            f'/api/tasks/{self.task.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['id'],
            self.task.id,
        )
        self.assertEqual(
            response.data['title'],
            'Test Task',
        )

    def test_get_task_as_non_member_forbidden(self):
        self.client.force_authenticate(
            user=self.outsider
        )

        response = self.client.get(
            f'/api/tasks/{self.task.id}/'
        )

        self.assertEqual(response.status_code, 403)

    def test_get_task_not_found(self):
        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.get(
            '/api/tasks/999/'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'Task not found.',
        )

    def test_update_task_requires_authentication(self):
        data = {
            'title': 'Updated Task',
        }

        response = self.client.patch(
            f'/api/tasks/{self.task.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_update_task_as_board_member(self):
        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'title': 'Updated Task',
            'priority': 'high',
        }

        response = self.client.patch(
            f'/api/tasks/{self.task.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['title'],
            'Updated Task',
        )
        self.assertEqual(
            response.data['priority'],
            'high',
        )

    def test_update_task_as_non_member_forbidden(self):
        self.client.force_authenticate(
            user=self.outsider
        )

        data = {
            'title': 'Forbidden Update',
        }

        response = self.client.patch(
            f'/api/tasks/{self.task.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_update_task_not_found(self):
        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'title': 'Updated Task',
        }

        response = self.client.patch(
            '/api/tasks/999/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'Task not found.',
        )

    def test_update_task_rejects_assignee_not_in_board(self):
        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'assignee_id': self.outsider.id,
        }

        response = self.client.patch(
            f'/api/tasks/{self.task.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'assignee_id',
            response.data,
        )

    def test_update_task_rejects_reviewer_not_in_board(self):
        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'reviewer_id': self.outsider.id,
        }

        response = self.client.patch(
            f'/api/tasks/{self.task.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'reviewer_id',
            response.data,
        )

    def test_delete_task_requires_authentication(self):
        response = self.client.delete(
            f'/api/tasks/{self.task.id}/'
        )

        self.assertEqual(response.status_code, 401)

    def test_delete_task_as_non_member_forbidden(self):
        self.client.force_authenticate(
            user=self.outsider
        )

        response = self.client.delete(
            f'/api/tasks/{self.task.id}/'
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_task_as_creator(self):
        self.client.force_authenticate(
            user=self.owner
        )

        task_id = self.task.id

        response = self.client.delete(
            f'/api/tasks/{task_id}/'
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Task.objects.filter(id=task_id).exists()
        )

    def test_delete_task_as_creator_removed_from_board(self):
        self.board.members.remove(self.owner)
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(
            f'/api/tasks/{self.task.id}/'
        )

        self.assertEqual(response.status_code, 204)

    def test_delete_task_as_creator_who_is_not_board_owner(self):
        task = Task.objects.create(
            board=self.board,
            title='Member-created task',
            description='Created by a board member.',
            status='to-do',
            priority='medium',
            creator=self.member,
        )
        self.client.force_authenticate(user=self.member)

        response = self.client.delete(f'/api/tasks/{task.id}/')

        self.assertEqual(response.status_code, 204)

    def test_delete_task_as_board_owner_who_is_not_creator(self):
        task = Task.objects.create(
            board=self.board,
            title='Member-created task',
            description='Created by a board member.',
            status='to-do',
            priority='medium',
            creator=self.member,
        )
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(f'/api/tasks/{task.id}/')

        self.assertEqual(response.status_code, 204)

    def test_delete_task_as_board_member_forbidden(self):
        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.delete(
            f'/api/tasks/{self.task.id}/'
        )

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            Task.objects.filter(id=self.task.id).exists()
        )

    def test_delete_task_not_found(self):
        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.delete(
            '/api/tasks/999/'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'Task not found.',
        )

    def test_get_comments_requires_authentication(self):
        response = self.client.get(
            f'/api/tasks/{self.task.id}/comments/'
        )

        self.assertEqual(response.status_code, 401)

    def test_get_comments_as_board_member(self):
        Comment.objects.create(
            task=self.task,
            author=self.member,
            content='Test Comment',
        )

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.get(
            f'/api/tasks/{self.task.id}/comments/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['content'],
            'Test Comment',
        )

    def test_get_comments_as_non_member_forbidden(self):
        self.client.force_authenticate(
            user=self.outsider
        )

        response = self.client.get(
            f'/api/tasks/{self.task.id}/comments/'
        )

        self.assertEqual(response.status_code, 403)

    def test_create_comment_as_board_member(self):
        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'content': 'New Test Comment',
        }

        response = self.client.post(
            f'/api/tasks/{self.task.id}/comments/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data['content'],
            'New Test Comment',
        )

    def test_create_comment_as_non_member_forbidden(self):
        self.client.force_authenticate(
            user=self.outsider
        )

        data = {
            'content': 'Forbidden Comment',
        }

        response = self.client.post(
            f'/api/tasks/{self.task.id}/comments/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_create_comment_rejects_missing_content(self):
        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.post(
            f'/api/tasks/{self.task.id}/comments/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'content',
            response.data,
        )

    def test_create_comment_task_not_found(self):
        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'content': 'Comment on missing task',
        }

        response = self.client.post(
            '/api/tasks/999/comments/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'Task not found.',
        )

    def test_get_comments_task_not_found(self):
        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.get(
            '/api/tasks/999/comments/'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'Task not found.',
        )

    def test_delete_comment_requires_authentication(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.member,
            content='Comment to delete',
        )

        response = self.client.delete(
            f'/api/tasks/{self.task.id}/comments/{comment.id}/'
        )

        self.assertEqual(response.status_code, 401)

    def test_delete_comment_as_non_member_forbidden(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.member,
            content='Protected Comment',
        )

        self.client.force_authenticate(
            user=self.outsider
        )

        response = self.client.delete(
            f'/api/tasks/{self.task.id}/comments/{comment.id}/'
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_comment_as_author(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.member,
            content='Comment to delete',
        )

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.delete(
            f'/api/tasks/{self.task.id}/comments/{comment.id}/'
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Comment.objects.filter(id=comment.id).exists()
        )

    def test_delete_comment_as_author_removed_from_board(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.member,
            content='Comment to delete',
        )
        self.board.members.remove(self.member)
        self.client.force_authenticate(user=self.member)

        response = self.client.delete(
            f'/api/tasks/{self.task.id}/comments/{comment.id}/'
        )

        self.assertEqual(response.status_code, 204)

    def test_delete_comment_as_other_board_member_forbidden(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.owner,
            content='Protected Comment',
        )

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.delete(
            f'/api/tasks/{self.task.id}/comments/{comment.id}/'
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Comment.objects.filter(id=comment.id).exists()
        )

    def test_delete_comment_not_found(self):
        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.delete(
            f'/api/tasks/{self.task.id}/comments/999/'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'Comment not found.',
        )

    def test_delete_comment_wrong_task_not_found(self):
        other_task = Task.objects.create(
            board=self.board,
            title='Other Task',
            description='Another task',
            status='to-do',
            creator=self.owner,
            priority='medium',
            assignee=self.member,
            reviewer=self.member,
        )

        comment = Comment.objects.create(
            task=other_task,
            author=self.member,
            content='Comment on other task',
        )

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.delete(
            f'/api/tasks/{self.task.id}/comments/{comment.id}/'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'Comment not found.',
        )
