from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from auth_app.models import User


class RegistrationViewTest(TestCase):

    def setUp(self):
        self.client=APIClient()

    def test_registration_success(self):
        data={
            'fullname': 'View Test User',
            'email': 'view@test.com',
            'password': 'password123',
            'repeated_password': 'password123',
        }

        response=self.client.post(
            '/api/registration/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            201,
        )
        self.assertEqual(
            response.data['email'],
            'view@test.com',
        )
        self.assertEqual(
            response.data['fullname'],
            'View Test User',
        )
        self.assertIn(
            'token',
            response.data,
        )
        self.assertTrue(
            Token.objects.filter(
                user__email='view@test.com',
            ).exists()
        )
        self.assertTrue(
            User.objects.filter(
                email='view@test.com',
            ).exists()
        )


    def test_registration_password_mismatch(self):
        data={
            'fullname': 'View Test User',
            'email': 'mismatch@test.com',
            'password': 'password123',
            'repeated_password': 'different123',
        }

        response=self.client.post(
            '/api/registration/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertIn(
            'password',
            response.data,
        )

    def test_registration_invalid_data(self):
        data = {
            'fullname': '',
            'email': 'invalid-registration@test.com',
            'password': 'password123',
            'repeated_password': 'password123',
        }

        response = self.client.post(
            '/api/registration/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            400,
        )

class LoginViewTest(TestCase):

    def setUp(self):
        self.client=APIClient()

        self.user=User.objects.create_user(
            email='login-view@test.com',
            password='password123',
            fullname='Login View User',
        )

    def test_login_success(self):
        data={
            'email': 'login-view@test.com',
            'password': 'password123',
        }

        response=self.client.post(
            '/api/login/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.data['email'],
            'login-view@test.com',
        )
        self.assertEqual(
            response.data['fullname'],
            'Login View User',
        )
        self.assertIn(
            'token',
            response.data,
        )
        self.assertTrue(
            Token.objects.filter(
                user=self.user,
            ).exists()
        )


    def test_login_invalid_password(self):
        data={
            'email': 'login-view@test.com',
            'password': 'wrongpassword',
        }

        response=self.client.post(
            '/api/login/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertIn(
            'non_field_errors',
            response.data,
        )

    def test_login_with_existing_token(self):
        Token.objects.create(user=self.user)

        data = {
            'email': 'login-view@test.com',
            'password': 'password123',
        }

        response = self.client.post(
            '/api/login/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertIn(
            'token',
            response.data,
        )

class EmailCheckViewTest(TestCase):

    def setUp(self):
        self.client=APIClient()

    def test_email_check_unauthenticated(self):
        response=self.client.get(
            '/api/email-check/',
            {'email': 'test@test.com'},
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_email_check_valid(self):
        user=User.objects.create_user(
            email='email-check@test.com',
            password='password123',
            fullname='Email Check User',
        )

        self.client.force_authenticate(user=user)

        response=self.client.get(
            '/api/email-check/',
            {'email': 'email-check@test.com'},
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.data,
            {
                'id': user.id,
                'email': 'email-check@test.com',
                'fullname': 'Email Check User',
            },
        )

    def test_email_check_invalid_email(self):
        user=User.objects.create_user(
            email='email-check@test.com',
            password='password123',
            fullname='Email Check User',
        )

        self.client.force_authenticate(user=user)

        response=self.client.get(
            '/api/email-check/',
            {'email': 'not-an-email'},
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertIn(
            'email',
            response.data,
        )

    def test_email_check_user_not_found(self):
        user=User.objects.create_user(
            email='existing@test.com',
            password='password123',
            fullname='Existing User',
        )

        self.client.force_authenticate(user=user)

        response=self.client.get(
            '/api/email-check/',
            {'email': 'unknown@test.com'},
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_email_check_missing_email(self):
        user = User.objects.create_user(
            email='email-check@test.com',
            password='password123',
            fullname='Email Check User',
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(
            '/api/email-check/',
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertIn(
            'email',
            response.data,
        )
