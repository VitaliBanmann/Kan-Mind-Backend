from django.test import TestCase

from auth_app.api.serializers import (
    UserSerializer,
    EmailCheckSerializer,
    LoginSerializer, 
    RegistrationSerializer,
)
from auth_app.models import User


class RegistrationSerializerTest(TestCase):

    def test_registration_serializer_valid(self):
        data={
            'fullname': 'Test User',
            'email': 'serializer@test.com',
            'password': 'password123',
            'repeated_password': 'password123',
        }

        serializer=RegistrationSerializer(data=data)

        self.assertTrue(serializer.is_valid())

        user=serializer.save()

        self.assertEqual(
            user.email,
            'serializer@test.com',
        )
        self.assertEqual(
            user.fullname,
            'Test User',
        )
        self.assertTrue(
            user.check_password('password123')
        )



    def test_registration_serializer_password_mismatch(self):
        data={
            'fullname': 'Test User',
            'email': 'serializer@test.com',
            'password': 'password123',
            'repeated_password': 'different123',
        }

        serializer=RegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            'password',
            serializer.errors,
        )



class LoginSerializerTest(TestCase):

    def setUp(self):
        self.user=User.objects.create_user(
            email='login@test.com',
            password='password123',
            fullname='Login User',
        )

    def test_login_serializer_valid(self):
        data={
            'email': 'login@test.com',
            'password': 'password123',
        }

        serializer=LoginSerializer(data=data)

        self.assertTrue(serializer.is_valid())

        self.assertEqual(
            serializer.validated_data['user'],
            self.user,
        )



    def test_login_serializer_invalid_password(self):
        data={
            'email': 'login@test.com',
            'password': 'wrongpassword',
        }

        serializer=LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            'non_field_errors',
            serializer.errors,
        )



    def test_login_serializer_unknown_email(self):
        data={
            'email': 'unknown@test.com',
            'password': 'password123',
        }

        serializer=LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            'non_field_errors',
            serializer.errors,
        )



class EmailCheckSerializerTest(TestCase):

    def test_email_check_serializer_valid(self):
        data={
            'email': 'valid@test.com',
        }

        serializer=EmailCheckSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data['email'],
            'valid@test.com',
        )



    def test_email_check_serializer_invalid(self):
        data={
            'email': 'not-an-email',
        }

        serializer=EmailCheckSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            'email',
            serializer.errors,
        )



class UserSerializerTest(TestCase):

    def test_user_serializer_returns_expected_fields(self):
        user=User.objects.create_user(
            email='serializer@test.com',
            password='TestPassword123',
            fullname='Serializer Test User',
        )

        serializer=UserSerializer(user)

        self.assertEqual(
            serializer.data,
            {
                'id': user.id,
                'email': 'serializer@test.com',
                'fullname': 'Serializer Test User',
            },
        )