from django.test import TestCase

from auth_app.models import User


class UserManagerTest(TestCase):

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='password123',
            )


    def test_create_superuser(self):
        user=User.objects.create_superuser(
            email='admin@test.com',
            password='password123',
        )

        self.assertTrue(
            user.is_staff,
        )
        self.assertTrue(
            user.is_superuser,
        )
        self.assertTrue(
            user.is_active,
        )
        self.assertTrue(
            user.check_password('password123'),
        )

    def test_create_user(self):
        user=User.objects.create_user(
            email='user@test.com',
            password='password123',
            fullname='Test User',
        )

        self.assertEqual(
            user.email,
            'user@test.com',
        )
        self.assertEqual(
            user.fullname,
            'Test User',
        )
        self.assertTrue(
            user.check_password('password123'),
        )