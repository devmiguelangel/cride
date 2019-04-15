""" User views """

# Django REST Framework
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# Serializers
from cride.users.serializers import (UserLoginSerializer, UserSignUpSerializer, AccountVerificationSerializer,
                                     UserModelSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """ User view set.

    Handle sign up, login and account verification.
    """

    @action(detail=False, methods=['post'])
    def login(self, request):
        """ User login API view. """

        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'token': token
        }

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def signup(self, request):
        """ User sign up API view. """

        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """ Account Verification API view. """

        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message': 'Congratulations, now go comparte some rides!'}

        return Response(data, status=status.HTTP_200_OK)
