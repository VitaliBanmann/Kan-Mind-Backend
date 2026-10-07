from django.test import TestCase
from rest_framework.test import APIClient

from auth_app.models import User
from board_app.models import Board
from task_app.models import Task, Comment


class BoardViewsTest(TestCase):

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

    def test_list_boards_returns_owned_boards(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.get('/api/boards/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['title'],
            'Test Board',
        )

    def test_list_boards_returns_member_boards(self):
        self.board.members.add(self.member)

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.get('/api/boards/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['title'],
            'Test Board',
        )

    def test_list_boards_requires_authentication(self):
        response = self.client.get('/api/boards/')

        self.assertEqual(response.status_code, 401)

    def test_create_board_requires_authentication(self):
        data = {
            'title': 'New Board',
        }

        response = self.client.post(
            '/api/boards/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_get_board_requires_authentication(self):
        response = self.client.get(
            f'/api/boards/{self.board.id}/'
        )

        self.assertEqual(response.status_code, 401)

    def test_update_board_requires_authentication(self):
        data = {
            'title': 'Updated Board',
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_create_board_success(self):
        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'title': 'New Board',
        }

        response = self.client.post(
            '/api/boards/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data['title'],
            'New Board',
        )

        self.assertEqual(
            response.data['owner_id'],
            self.owner.id,
        )

        self.assertTrue(
            Board.objects.filter(
                title='New Board',
                owner=self.owner,
            ).exists()
        )

    def test_create_board_with_members(self):
        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'title': 'Board With Members',
            'members': [self.member.id],
        }

        response = self.client.post(
            '/api/boards/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 201)

        board = Board.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            board.title,
            'Board With Members',
        )

        self.assertIn(
            self.member,
            board.members.all(),
        )

        self.assertEqual(
            board.owner,
            self.owner,
        )

    def test_create_board_with_owner_as_member(self):
        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'title': 'Board With Owner',
            'members': [self.owner.id],
        }

        response = self.client.post(
            '/api/boards/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 201)

        board = Board.objects.get(
            id=response.data['id']
        )

        self.assertIn(
            self.owner,
            board.members.all(),
        )

    def test_create_board_with_invalid_member(self):
        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'title': 'Board With Invalid Member',
            'members': [99999],
        }

        response = self.client.post(
            '/api/boards/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 400)

        self.assertFalse(
            Board.objects.filter(
                title='Board With Invalid Member'
            ).exists()
        )

    def test_create_board_invalid_data(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.post(
            '/api/boards/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)

    def test_get_board_details_as_owner(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.get(
            f'/api/boards/{self.board.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['id'],
            self.board.id,
        )

        self.assertEqual(
            response.data['title'],
            'Test Board',
        )

        self.assertEqual(
            response.data['owner_id'],
            self.owner.id,
        )

    def test_get_board_details_as_member(self):
        self.board.members.add(self.member)

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.get(
            f'/api/boards/{self.board.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['id'],
            self.board.id,
        )

        self.assertEqual(
            response.data['title'],
            'Test Board',
        )

    def test_get_board_as_non_member_forbidden(self):
        self.client.force_authenticate(
            user=self.outsider
        )

        response = self.client.get(
            f'/api/boards/{self.board.id}/'
        )

        self.assertEqual(response.status_code, 403)

    def test_update_board_as_non_member_forbidden(self):
        self.client.force_authenticate(
            user=self.outsider
        )

        data = {
            'title': 'Forbidden Update',
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_get_board_not_found(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.get(
            '/api/boards/99999/'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'Board not found',
        )

    def test_update_board_success(self):
        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'title': 'Updated Board',
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['title'],
            'Updated Board',
        )

        self.board.refresh_from_db()

        self.assertEqual(
            self.board.title,
            'Updated Board',
        )

    def test_update_board_invalid_data(self):
        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'title': 'A' * 151,
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)

    def test_update_board_not_found(self):
        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'title': 'Updated Board',
        }

        response = self.client.patch(
            '/api/boards/99999/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'Board not found',
        )

    def test_delete_board_requires_authentication(self):
        response = self.client.delete(
            f'/api/boards/{self.board.id}/'
        )

        self.assertEqual(response.status_code, 401)

    def test_delete_board_success(self):
        self.client.force_authenticate(
            user=self.owner
        )

        board_id = self.board.id

        response = self.client.delete(
            f'/api/boards/{board_id}/'
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Board.objects.filter(id=board_id).exists()
        )

    def test_delete_board_not_found(self):
        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.delete(
            '/api/boards/99999/'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'Board not found',
        )

    def test_delete_board_permission_denied(self):
        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.delete(
            f'/api/boards/{self.board.id}/'
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data['detail'],
            'Permission denied',
        )

        self.assertTrue(
            Board.objects.filter(
                id=self.board.id
            ).exists()
        )

    def test_update_board_as_member(self):
        self.board.members.add(self.member)

        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'title': 'Updated By Member',
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['title'],
            'Updated By Member',
        )

    def test_update_board_adds_member(self):
        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'members': [self.member.id],
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.board.refresh_from_db()

        self.assertIn(
            self.member,
            self.board.members.all(),
        )

    def test_update_board_removes_member(self):
        self.board.members.add(self.member)

        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'members': [],
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.board.refresh_from_db()

        self.assertNotIn(
            self.member,
            self.board.members.all(),
        )

    def test_update_board_removes_member(self):
        self.board.members.add(self.member)

        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'members': [],
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.board.refresh_from_db()

        self.assertNotIn(
            self.member,
            self.board.members.all(),
        )

    def test_update_board_rejects_invalid_member(self):
        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'members': [99999],
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'members',
            response.data,
        )

    def test_update_board_replaces_members(self):
        self.board.members.add(
            self.member,
            self.outsider,
        )

        self.client.force_authenticate(
            user=self.owner
        )

        data = {
            'members': [self.member.id],
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.board.refresh_from_db()

        self.assertIn(
            self.member,
            self.board.members.all(),
        )

        self.assertNotIn(
            self.outsider,
            self.board.members.all(),
        )

    def test_update_board_as_member_adds_member(self):
        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'members': [self.outsider.id],
        }

        self.board.members.add(self.member)

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.board.refresh_from_db()

        self.assertIn(
            self.outsider,
            self.board.members.all(),
        )

    def test_list_boards_excludes_unrelated_boards(self):
        other_board = Board.objects.create(
            title='Other Board',
            owner=self.outsider,
        )

        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.get('/api/boards/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['id'],
            self.board.id,
        )
        self.assertNotEqual(
            response.data[0]['id'],
            other_board.id,
        )

    def test_update_board_as_member_removes_other_member(self):
        self.board.members.add(
            self.member,
            self.outsider,
        )

        self.client.force_authenticate(
            user=self.member
        )

        data = {
            'members': [self.member.id],
        }

        response = self.client.patch(
            f'/api/boards/{self.board.id}/',
            data,
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.board.refresh_from_db()

        self.assertIn(
            self.member,
            self.board.members.all(),
        )

        self.assertNotIn(
            self.outsider,
            self.board.members.all(),
        )

    def test_get_board_details_includes_members_and_tasks(self):
        self.board.members.add(self.member)

        task = Task.objects.create(
            board=self.board,
            title='Board Task',
            description='Task for board details',
            status='to-do',
            priority='high',
            creator=self.owner,
            assignee=self.member,
            reviewer=self.member,
            due_date='2026-08-20',
        )

        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.get(
            f'/api/boards/{self.board.id}/'
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data['members']),
            1,
        )

        self.assertEqual(
            response.data['members'][0]['id'],
            self.member.id,
        )

        self.assertEqual(
            len(response.data['tasks']),
            1,
        )

        self.assertEqual(
            response.data['tasks'][0]['id'],
            task.id,
        )

        self.assertEqual(
            response.data['tasks'][0]['title'],
            'Board Task',
        )

    def test_get_board_details_includes_task_details(self):
        self.board.members.add(self.member)

        task = Task.objects.create(
            board=self.board,
            title='Detailed Task',
            description='Detailed Description',
            status='review',
            priority='high',
            creator=self.owner,
            assignee=self.member,
            reviewer=self.member,
            due_date='2026-08-20',
        )

        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.get(
            f'/api/boards/{self.board.id}/'
        )

        self.assertEqual(response.status_code, 200)

        task_data = response.data['tasks'][0]

        self.assertEqual(
            task_data['id'],
            task.id,
        )

        self.assertEqual(
            task_data['title'],
            'Detailed Task',
        )

        self.assertEqual(
            task_data['description'],
            'Detailed Description',
        )

        self.assertEqual(
            task_data['status'],
            'review',
        )

        self.assertEqual(
            task_data['priority'],
            'high',
        )

        self.assertEqual(
            task_data['assignee']['id'],
            self.member.id,
        )

        self.assertEqual(
            task_data['reviewer']['id'],
            self.member.id,
        )

        self.assertEqual(
            task_data['due_date'],
            '2026-08-20',
        )

        self.assertEqual(
            task_data['comments_count'],
            0,
        )

    def test_get_board_details_returns_correct_comments_count(self):
        self.board.members.add(self.member)

        task = Task.objects.create(
            board=self.board,
            title='Task With Comments',
            description='Task with comments',
            status='to-do',
            priority='medium',
            creator=self.owner,
            assignee=self.member,
            reviewer=self.member,
            due_date='2026-08-20',
        )

        Comment.objects.create(
            task=task,
            author=self.owner,
            content='First comment',
        )

        Comment.objects.create(
            task=task,
            author=self.member,
            content='Second comment',
        )

        Comment.objects.create(
            task=task,
            author=self.owner,
            content='Third comment',
        )

        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.get(
            f'/api/boards/{self.board.id}/'
        )

        self.assertEqual(response.status_code, 200)

        task_data = response.data['tasks'][0]

        self.assertEqual(
            task_data['id'],
            task.id,
        )

        self.assertEqual(
            task_data['comments_count'],
            3,
        )
