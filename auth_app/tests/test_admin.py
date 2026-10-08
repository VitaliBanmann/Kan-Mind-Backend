from django.contrib import admin
from django.test import RequestFactory, TestCase

from auth_app.forms import CustomUserCreationForm
from auth_app.models import User


class CustomUserAdminTest(TestCase):

    def test_admin_forms_use_email_and_fullname_without_username(self):
        user_admin = admin.site._registry[User]
        request = RequestFactory().get('/admin/')
        request.user = User.objects.create_superuser(
            email='admin@example.com',
            password='KanMind-Admin-Setup-2026!',
            fullname='KanMind Admin',
        )
        add_form = user_admin.get_form(request=request, change=False)
        change_form = user_admin.get_form(
            request=request,
            obj=User(email='user@example.com', fullname='Test User'),
        )

        self.assertIn('email', add_form.base_fields)
        self.assertIn('fullname', add_form.base_fields)
        self.assertNotIn('username', add_form.base_fields)
        self.assertIn('fullname', change_form.base_fields)
        self.assertNotIn('username', change_form.base_fields)

    def test_admin_creation_form_hashes_password(self):
        raw_password = 'KanMind-Admin-Setup-2026!'
        form = CustomUserCreationForm(data={
            'email': 'admin@example.com',
            'fullname': 'KanMind Admin',
            'password1': raw_password,
            'password2': raw_password,
        })

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertTrue(user.check_password(raw_password))
        self.assertNotEqual(user.password, raw_password)
