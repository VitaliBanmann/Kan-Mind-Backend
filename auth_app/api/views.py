from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from ..models import User
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    EmailCheckSerializer
)


class RegistrationView(APIView):
    """Handle user registration and token creation."""

    permission_classes = []

    def post(self, request):
        """Create a new user and return an authentication token."""
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.create(user=user)
            return Response(
                {
                    'token': token.key,
                    'fullname': user.fullname,
                    'email': user.email,
                    'user_id': user.id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    """Handle user authentication and token retrieval."""

    permission_classes = []

    def post(self, request):
        """Authenticate a user and return an authentication token."""
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)

            return Response(
                {
                    'token': token.key,
                    'fullname': user.fullname,
                    'email': user.email,
                    'user_id': user.id,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class EmailCheckView(APIView):
    """Handle authenticated requests for user email lookups."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return basic user information for a given email address."""
        serializer = EmailCheckSerializer(data=request.query_params)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(
            User,
            email=serializer.validated_data['email'],
        )

        return Response(
            {
                'id': user.id,
                'email': user.email,
                'fullname': user.fullname,
            },
            status=status.HTTP_200_OK,
        )
