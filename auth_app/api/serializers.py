from rest_framework import serializers
from django.contrib.auth import authenticate

from ..models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate and create new KanMind user accounts."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'fullname',
            'email',
            'password',
            'repeated_password',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """Ensure that both submitted passwords are identical."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'password': 'Password´s don´t match.'}
            )
        return attrs

    def create(self, validated_data):
        """Create a user from the validated registration data."""
        validated_data.pop('repeated_password')

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            fullname=validated_data['fullname'],
        )

        return user


class LoginSerializer(serializers.Serializer):
    """Validate login credentials and authenticate a user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the user with the submitted credentials."""
        user = authenticate(
            email=attrs['email'],
            password=attrs['password'],
        )

        if user is None:
            raise serializers.ValidationError('Invalid email or password.')

        attrs['user'] = user
        return attrs


class EmailCheckSerializer(serializers.Serializer):
    """Validate an email address used for user lookup."""

    email = serializers.EmailField()


class UserSerializer(serializers.ModelSerializer):
    """Serialize basic user information for API responses."""

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'fullname',
        ]
