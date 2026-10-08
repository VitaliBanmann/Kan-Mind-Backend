from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    username = None

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'fullname')


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'
